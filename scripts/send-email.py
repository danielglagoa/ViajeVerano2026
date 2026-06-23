"""
Envía el email de resultados de búsqueda de alojamiento via Gmail SMTP.
Se ejecuta desde el workflow de GitHub Actions tras la búsqueda de Claude.
Requiere variables de entorno: GMAIL_USER, GMAIL_APP_PASSWORD.
"""

import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

RECIPIENT = "danielglagoa@gmail.com"
SUBJECT_FILE = Path("logs/email-subject.txt")
BODY_FILE = Path("logs/email-body.txt")


def main():
    gmail_user = os.environ.get("GMAIL_USER", "").strip()
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not gmail_user or not gmail_password:
        print("ERROR: Faltan GMAIL_USER o GMAIL_APP_PASSWORD.", file=sys.stderr)
        sys.exit(1)

    if not BODY_FILE.exists():
        print(f"ERROR: No existe {BODY_FILE}.", file=sys.stderr)
        sys.exit(1)

    subject = (
        SUBJECT_FILE.read_text(encoding="utf-8").strip()
        if SUBJECT_FILE.exists()
        else "Búsqueda alojamiento Valencia/Gandía"
    )
    body = BODY_FILE.read_text(encoding="utf-8")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = RECIPIENT
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, [RECIPIENT], msg.as_string())
        print(f"✅ Email enviado a {RECIPIENT}")
        print(f"   Asunto: {subject}")
    except smtplib.SMTPException as exc:
        print(f"ERROR al enviar email: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
