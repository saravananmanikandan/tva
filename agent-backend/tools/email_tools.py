# tools/email_tools.py

import smtplib
from email.mime.text import MIMEText
import os

FROM_EMAIL = os.getenv("FROM_EMAIL")        # e.g. your Gmail address
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Gmail App Password

def send_violation_email(to_email: str, subject: str, body: str):
    """
    Sends an email using Gmail SMTP (App Password approach).
    Works on Cloud Run.
    """
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(FROM_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)

        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
