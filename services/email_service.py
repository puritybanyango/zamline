# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access

import smtplib
from email.message import EmailMessage

from config import (
    EMAIL_FROM,
    EMAIL_HOST,
    EMAIL_PASSWORD,
    EMAIL_PORT,
    EMAIL_USERNAME,
    EMAIL_USE_TLS,
)


def send_otp_email(recipient: str, code: str) -> None:
    if not EMAIL_HOST or not EMAIL_FROM:
        raise RuntimeError("Email delivery is not configured")

    message = EmailMessage()
    message["Subject"] = "Your ZamLine verification code"
    message["From"] = EMAIL_FROM
    message["To"] = recipient
    message.set_content(
        f"Your ZamLine verification code is {code}. "
        "Use it before it expires. Do not share this code."
    )

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=20) as server:
        if EMAIL_USE_TLS:
            server.starttls()
        if EMAIL_USERNAME:
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(message)
