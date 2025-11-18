# tools/email_tools.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart  # HTML support
import os

FROM_EMAIL = os.getenv("FROM_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_violation_email(to_email: str, subject: str, body: str):
    try:
        # Allow HTML formatting
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email

        html_body = f"""
        <html>
        <body>
            <h2 style="color:red;">🚨 Traffic Violation Detected</h2>
            <p><b>{body}</b></p>
            <p>Please take appropriate actions.</p>
            <hr>
            <p>TVA System • AI Powered Detection</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, "plain"))
        msg.attach(MIMEText(html_body, "html"))  # HTML email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(FROM_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)

        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
