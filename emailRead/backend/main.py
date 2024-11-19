import imaplib
import email
from email.header import decode_header
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from cachetools import TTLCache
from concurrent.futures import ThreadPoolExecutor
import threading

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
    date: Optional[str] = None

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

def fetch_email_batch(msg_nums: List[bytes], keyword: Optional[str] = None) -> List[EmailSubjectResponse]:
    """Fetch a batch of emails using a single thread"""
    emails = []
    try:
        mail = get_imap_connection()
        for msg_num in msg_nums:
            cache_key = f"{msg_num.decode()}"
            cached_email = email_cache.get(cache_key)
            
            if cached_email:
                if keyword is None or keyword.lower() in cached_email.subject.lower():
                    emails.append(cached_email)
                continue

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
                    email_resp = EmailSubjectResponse(
                        email_id=msg_num.decode(),
                        subject=subject,
                        date=date_str
                    )
                    
                    # Cache the email
                    email_cache[cache_key] = email_resp
                    
                    if keyword is None or keyword.lower() in subject.lower():
                        emails.append(email_resp)
                    break

    except Exception as e:
        print(f"Error in batch processing: {e}")
    
    return emails

async def fetch_emails(keyword: str, limit: int = 10) -> List[EmailSubjectResponse]:
    """Fetch emails with parallel processing and caching"""
    try:
        mail = imaplib.IMAP4_SSL(server)
        mail.login(email_user, email_pass)
        mail.select(folder)

        # Search for all email IDs
        status, messages = mail.search(None, "ALL")
        if status != "OK":
            raise HTTPException(status_code=404, detail="No messages found")

        message_nums = messages[0].split()
        if limit:
            message_nums = message_nums[-limit:]

        # Split messages into batches for parallel processing
        batch_size = 10
        batches = [message_nums[i:i + batch_size] for i in range(0, len(message_nums), batch_size)]

        # Process batches in parallel using ThreadPoolExecutor
        email_subjects = []
        futures = []
        
        for batch in batches:
            future = executor.submit(fetch_email_batch, batch, keyword)
            futures.append(future)

        # Gather results
        for future in futures:
            email_subjects.extend(future.result())

        mail.logout()
        return email_subjects

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching emails")

async def fetch_email_by_id(email_id: str) -> dict:
    """Fetch single email with caching"""
    cache_key = f"detail_{email_id}"
    cached_email = detail_cache.get(cache_key)
    if cached_email:
        return cached_email

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

                # Cache the result
                detail_cache[cache_key] = email_detail
                return email_detail

        mail.logout()

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching the email")

@app.get("/emails/all", response_model=List[EmailSubjectResponse])
async def get_email_subjects(limit: Optional[int] = None):
    """Get all email subjects"""
    return await fetch_emails(None, limit=limit)

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