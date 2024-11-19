import imaplib
import email
from email.header import decode_header
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware

# Environment variables for email credentials
server = os.getenv("IMAP_SERVER", "imap.gmail.com")
email_user = os.getenv("EMAIL_USER", "ashishkhuranatalentelgia@gmail.com")
email_pass = os.getenv("EMAIL_PASS", "sufc vywh pcxe lnes")
folder = os.getenv("EMAIL_FOLDER", "INBOX")
email_limit = int(os.getenv("EMAIL_LIMIT", 100))
# keyword = os.getenv("KEYWORD", "ATS")
email_check_interval = int(os.getenv("EMAIL_CHECK_INTERVAL", 30))
retry_interval = int(os.getenv("RETRY_INTERVAL", 60))  # Time between retries if connection fails

app = FastAPI()

origins = [
    "http://localhost",  # Allow localhost for development
    "http://localhost:8000",  # Allow FastAPI's own origin (if the front-end and back-end are hosted on the same server)
    "*",  # Allow all origins (you can specify your front-end URL here instead of "*" for better security)
]

# Add CORSMiddleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all or specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods like GET, POST, etc.
    allow_headers=["*"],  # Allows all headers
)

class EmailSubjectResponse(BaseModel):
    subject: str
    email_id: str


async def fetch_emails(keyword: str, offset: int = 0, limit: int = 10):
    """
    Fetch email subjects from the IMAP server asynchronously, with pagination.
    Args:
        keyword (str): Keyword to filter email subjects. If None, fetch all emails.
        offset (int): The starting position of the emails to fetch.
        limit (int): The number of emails to fetch.
    """
    email_subjects = []
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        # Search for all emails in the mailbox
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            raise HTTPException(status_code=404, detail="No messages found")

        messages = messages[0].split()
        total_emails = len(messages)
        print(f"Total emails in the folder: {total_emails}")

        # Adjust offset and limit
        start = max(0, total_emails - (offset + limit))
        end = max(0, total_emails - offset)
        selected_messages = messages[0:limit]

        print(f"Fetching emails {start + 1} to {end}...")

        for msg_num in selected_messages:
            # Fetch the email by ID
            status, msg_data = mail.fetch(msg_num, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse the email content
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")

                    # Check if the subject contains the keyword
                    if keyword is not None:
                        if keyword.lower() in subject.lower():
                            email_subjects.append(
                                EmailSubjectResponse(
                                    email_id=msg_num.decode(),  # Email ID as string
                                    subject=subject,
                                )
                            )
                    else:
                        email_subjects.append(
                                EmailSubjectResponse(
                                    email_id=msg_num.decode(),  # Email ID as string
                                    subject=subject,
                                )
                            )
        mail.logout()

    except (imaplib.IMAP4_SSL.error, imaplib.IMAP4.error) as e:
        print(f"Error connecting to IMAP server: {e}")
        raise HTTPException(status_code=500, detail="IMAP server connection failed")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching emails")

    return email_subjects

async def fetch_email_by_id(email_id: str):
    """
    Fetch the complete email details by its ID.
    Args:
        email_id (str): The unique ID of the email to fetch.
    Returns:
        dict: A dictionary containing email details like subject, sender, recipients, and body.
    """
    try:
        # Connect to the IMAP server
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        # Fetch the email by its ID
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            raise HTTPException(status_code=404, detail=f"Email with ID {email_id} not found")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                # Parse the email content
                msg = email.message_from_bytes(response_part[1])

                # Extract details
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                from_ = msg.get("From")
                to = msg.get("To")
                date = msg.get("Date")

                # Get the email body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))

                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                # Return the email details
                return {
                    "email_id": email_id,
                    "subject": subject,
                    "from": from_,
                    "to": to,
                    "date": date,
                    "body": body,
                }

        mail.logout()

    except (imaplib.IMAP4_SSL.error, imaplib.IMAP4.error) as e:
        print(f"Error connecting to IMAP server: {e}")
        raise HTTPException(status_code=500, detail="IMAP server connection failed")

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the email")


@app.get("/emails/all", response_model=list[EmailSubjectResponse])
async def get_email_subjects(limit: int | None = None):
    """
    Fetch email subjects from the mail server and return them based on whether they contain the keyword.
    This will return the email subjects as a JSON response.
    """
    if limit is not None:
        email_subjects = await fetch_emails(None, limit=limit)
    else:
        email_subjects = await fetch_emails(None)
    return email_subjects

@app.get("/emails/{keyword}", response_model=list[EmailSubjectResponse])
async def get_email_subjects(keyword:str, limit: int | None = None):
    """
    Fetch email subjects from the mail server and return them based on whether they contain the keyword.
    This will return the email subjects as a JSON response.
    """
    if limit is not None:
        email_subjects = await fetch_emails(keyword, limit=limit)
    else:
        email_subjects = await fetch_emails(keyword)
    return email_subjects


@app.get("/email/{email_id}", response_model=dict)
async def get_email_by_id(email_id: str):
    """
    Fetch a single email's complete details by its ID.
    Args:
        email_id (str): The unique ID of the email to fetch.
    Returns:
        dict: A dictionary containing email details like subject, sender, recipients, and body.
    """
    email_details = await fetch_email_by_id(email_id)
    return email_details

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
