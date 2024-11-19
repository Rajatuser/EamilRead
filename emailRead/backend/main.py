import imaplib
import email
from email.header import decode_header
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor
import threading
import re

# Environment variables
server = os.getenv("IMAP_SERVER", "imap.gmail.com")
email_user = os.getenv("EMAIL_USER", "ashishkhuranatalentelgia@gmail.com")
email_pass = os.getenv("EMAIL_PASS", "sufc vywh pcxe lnes")
folder = os.getenv("EMAIL_FOLDER", "INBOX")
cache_ttl = int(os.getenv("CACHE_TTL", 300))  # Cache timeout in seconds
max_workers = int(os.getenv("MAX_WORKERS", 5))  # Maximum number of thread workers

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
    date: str
    urgent: bool
    sku: Optional[str] = None
    
# Initialize caches with TTL
email_cache = TTLCache(maxsize=1000, ttl=cache_ttl)
detail_cache = TTLCache(maxsize=500, ttl=cache_ttl)
thread_local = threading.local()
executor = ThreadPoolExecutor(max_workers=max_workers)

def get_imap_connection():
    """Create and return a thread-local IMAP connection"""
    if not hasattr(thread_local, "imap"):
        thread_local.imap = imaplib.IMAP4_SSL(server)
        thread_local.imap.login(email_user, email_pass)
        thread_local.imap.select(folder)
    return thread_local.imap

def fetch_email_batch(msg_nums: List[bytes], keyword: Optional[str] = None, limit: int = 50) -> List[EmailSubjectResponse]:
    """Fetch a batch of emails using a single thread."""
    emails = []
    urgency_terms = [
        "Immediate", "Critical", "Important", "Pressing", "Emergency", "Hasty", "Swift",
        "Quick", "Instant", "Rapid", "Fast", "Alarming", "Dire", "Priority", "Vital",
        "Exigent", "Necessary", "Expedite", "Crucial", "Rush", "Time-sensitive", "Prompt",
        "On-demand", "Essential", "Imperative", "High-priority", "Flash", "Accelerate",
        "Severe", "Pinnacle", "Burning", "Urgency", "Urgent", "Unavoidable", "Must-do", "Grave",
        "Immediate-action", "Top-priority", "Demanding", "Overdue", "Peak", "Now",
        "Deadline-driven", "Accelerated", "Mandatory", "Pivotal", "Clamoring",
        "Necessary-action", "Alarmed", "Speedy", "Deadline-critical"
    ]
    # SKU pattern (matches SKUs anywhere in the subject)
    sku_pattern = r"[A-Z]{2}-[A-Z]{2}-[A-Z]{1,3}-\d{6}"
    today = datetime.today()

    # Subtract 50 days (as per original code)
    date_50_days_before = today - timedelta(days=50)

    # Convert to the desired format
    formatted_date = date_50_days_before.strftime("%d-%b-%Y")
    
    try:
        mail = get_imap_connection()
        result, data = mail.search(None, 'SINCE', str(formatted_date))
        
        if result == 'OK':
            total_emails = len(data[0].split())  # Get the total number of emails
            # Update the limit if there are fewer emails than the current limit
            adjusted_limit = min(limit, total_emails)
            msg_nums = data[0].split()[-adjusted_limit:]  # Fetch the latest 'adjusted_limit' emails
            
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
                        urgent = any(term.lower() in subject.lower() for term in urgency_terms)

                        # Extract SKU if it matches the pattern
                        sku_match = re.search(sku_pattern, subject)
                        sku = sku_match.group(0) if sku_match else None

                        email_resp = EmailSubjectResponse(
                            email_id=msg_num.decode(),
                            subject=subject,
                            date=date_str,
                            urgent=urgent,
                            sku=sku  # Add SKU to the response
                        )

                        # Only add email if it matches the keyword or keyword is None
                        if keyword is None or keyword.lower() in subject.lower():
                            emails.insert(0, email_resp)  # Insert at the beginning of the list

    except Exception as e:
        print(f"Error in batch processing: {e}")

    return emails


def fetch_emails(keyword: str, limit: int = 10) -> List[EmailSubjectResponse]:
    """Fetch emails with parallel processing and caching"""
    try:

        email_subjects = fetch_email_batch([], keyword, limit)

        return email_subjects

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching emails")

async def fetch_email_by_id(email_id: str) -> dict:
    """Fetch single email with caching"""
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        status, msg_data = mail.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                # Extract email details
                email_detail = {
                    "email_id": email_id,
                    "subject": subject,
                    "from": msg.get("From"),
                    "to": msg.get("To"),
                    "date": msg.get("Date"),
                    "body": "",
                }

                # Get email body
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                            email_detail["body"] = part.get_payload(decode=True).decode()
                            break
                else:
                    email_detail["body"] = msg.get_payload(decode=True).decode()
                return email_detail

        mail.logout()

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the email")

@app.get("/emails/all", response_model=List[EmailSubjectResponse])
async def get_email_subjects(limit: Optional[int] = None):
    """Get all email subjects"""
    return fetch_emails(None, limit=limit)

@app.get("/emails/{keyword}", response_model=List[EmailSubjectResponse])
async def get_email_subjects(keyword: str, limit: Optional[int] = None):
    """Get filtered email subjects"""
    return await fetch_emails(keyword, limit=limit)

@app.get("/email/{email_id}")
async def get_email_by_id(email_id: str):
    """Get single email details"""
    return await fetch_email_by_id(email_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)