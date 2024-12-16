import imaplib
import email
from email.header import decode_header
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
from typing import Optional, List
import re
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

# Environment variables
server = os.getenv("IMAP_SERVER")
email_user = os.getenv("EMAIL_USER")
email_pass = os.getenv("EMAIL_PASS")
folder = os.getenv("EMAIL_FOLDER")

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailSubjectResponse(BaseModel):
    subject: str
    email_id: str
    From: str
    date: str
    urgent: bool
    sku: Optional[str] = None

def get_imap_connection():
    """Create and return a new IMAP connection."""
    mail = imaplib.IMAP4_SSL(server)
    mail.login(email_user, email_pass)
    mail.select(folder)
    return mail

def fetch_email_batch(keyword: Optional[str] = None, limit: int = 50, formatted_date: str = None) -> List[EmailSubjectResponse]:
    """Fetch a batch of emails."""
    emails = []
    urgency_terms = [
        "Immediate", "Critical", "Important", "Pressing", "Emergency", "Hasty", "Swift",
        "Quick", "Instant", "Rapid", "Fast", "Alarming", "Dire", "Priority", "Vital",
        "Exigent", "Necessary", "Expedite", "Crucial", "Rush", "Time-sensitive", "Prompt",
        "On-demand", "Essential", "Imperative", "High-priority", "Flash", "Accelerate",
        "Severe", "Pinnacle", "Burning", "Urgency", "Urgent", "Unavoidable", "Must-do", "Grave",
        "Immediate-action", "Top-priority", "Demanding", "Overdue", "Peak", "Now",
        "Deadline-driven", "Accelerated", "Mandatory", "Pivotal", "Clamoring",
        "Necessary-action", "Alarmed", "Speedy", "Deadline-critical", "ASAP", "Action Needed","Alert","Security"
    ]
    sku_pattern = r"\b(?:SKU-?\d+|[A-Z0-9-]{5,})\b"
    
    try:
        # Ensure limit is not None
        limit = limit or 50  # Default limit to 50 if None
        mail = get_imap_connection()
        result, data = mail.search(None, 'SINCE', formatted_date)

        if result == 'OK':
            total_emails = len(data[0].split())
            adjusted_limit = min(limit, total_emails)
            msg_nums = data[0].split()[-adjusted_limit:]

            for msg_num in msg_nums:
                status, msg_data = mail.fetch(msg_num, "(RFC822.HEADER)")
                if status != "OK":
                    continue

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")

                        date_str = msg.get("Date")
                        from_data = msg.get("From")
                        urgent = any(term.lower() in subject.lower() for term in urgency_terms)

                        sku_match = re.search(sku_pattern, subject)
                        sku = sku_match.group(0) if sku_match else None

                        email_resp = EmailSubjectResponse(
                            email_id=msg_num.decode(),
                            subject=subject,
                            date=date_str,
                            From=from_data,
                            urgent=urgent,
                            sku=sku,
                        )

                        if keyword is None or keyword.lower() in subject.lower():
                            emails.insert(0, email_resp)
        mail.logout()
    except Exception as e:
        print(f"Error in batch processing: {e}")
    pprint(emails)
    return emails


def fetch_email_by_id(email_id: str) -> dict:
    """Fetch a single email by ID."""
    try:
        mail = get_imap_connection()
        status, msg_data = mail.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                email_detail = {
                    "email_id": email_id,
                    "subject": subject,
                    "from": msg.get("From"),
                    "to": msg.get("To"),
                    "date": msg.get("Date"),
                    "body": "",
                }

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                            email_detail["body"] = part.get_payload(decode=True).decode()
                            break
                else:
                    email_detail["body"] = msg.get_payload(decode=True).decode()
                mail.logout()
                return email_detail

        mail.logout()
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the email")

@app.get("/emails/all", response_model=List[EmailSubjectResponse])
async def get_email_subjects(checkDate: Optional[str] = None, limit: Optional[int] = None):
    """Get all email subjects with optional date filtering."""
    if checkDate is None:
        # If checkDate is not provided, set it to 40 days before the current date
        checkDate = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        print(f"No checkDate provided. Defaulting to {checkDate}")
        
    formatted_date = datetime.strptime(checkDate, "%Y-%m-%d").strftime("%d-%b-%Y")
    return fetch_email_batch(None, limit=limit, formatted_date=formatted_date)


@app.get("/emails/{keyword}", response_model=List[EmailSubjectResponse])
async def get_email_subjects(keyword: str, checkDate: Optional[str] = None, limit: Optional[int] = None):
    """Get filtered email subjects with optional date filtering."""
    if checkDate is None:
        # If checkDate is not provided, set it to 40 days before the current date
        checkDate = (datetime.now() - timedelta(days=40)).strftime("%Y-%m-%d")
        print(f"No checkDate provided. Defaulting to {checkDate}")
        
    formatted_date = datetime.strptime(checkDate, "%Y-%m-%d").strftime("%d-%b-%Y")
    return fetch_email_batch(keyword, limit=limit, formatted_date=formatted_date)

@app.get("/email/{email_id}")
async def get_email_by_id(email_id: str):
    """Get single email details."""
    return fetch_email_by_id(email_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
