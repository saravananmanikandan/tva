import os
import base64
from email.mime.text import MIMEText
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account JSON file (mounted via env variable)
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Email will be sent FROM this address (your service account email)
FROM_EMAIL = os.getenv("FROM_EMAIL")   # e.g., my-service@project-id.iam.gserviceaccount.com

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _create_message(to_email: str, subject: str, body_text: str):
    message = MIMEText(body_text)
    message["to"] = to_email
    message["from"] = FROM_EMAIL
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using Gmail API through a service account.
    This works WITHOUT OAuth and WITHOUT login, perfect for Cloud Run.
    """
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    # Build Gmail API client
    service = build("gmail", "v1", credentials=creds)

    # Prepare email
    message = _create_message(to_email, subject, body)

    # Send
    sent = (
        service.users()
        .messages()
        .send(userId="me", body=message)
        .execute()
    )

    return {"status": "sent", "message_id": sent.get("id")}
