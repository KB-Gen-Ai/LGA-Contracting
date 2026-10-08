import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def get_secret(key, default=None):
    """Get a secret from Streamlit secrets or environment variables."""
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

def send_email(recipients, subject, html_body):
    sender = get_secret("SENDER_EMAIL")
    password = get_secret("SENDER_PASSWORD")
    smtp_server = get_secret("SMTP_SERVER", "smtp.mail.yahoo.com")
    smtp_port = int(get_secret("SMTP_PORT", 465))

    if not sender or not password:
        raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must be set in secrets.")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(sender, password)
        server.sendmail(sender, recipients, msg.as_string())

    print(f"Email sent to: {recipients}")
