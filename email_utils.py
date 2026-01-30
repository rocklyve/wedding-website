import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_confirmation_email(to_email, subject, body):
    smtp = st.secrets["smtp"]
    smtp_host = smtp["host"]
    smtp_port = int(smtp.get("port", 587))
    smtp_user = smtp["user"]
    smtp_password = smtp["password"]
    from_email = smtp.get("from", smtp_user)

    msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"SMTP Fehler: {e}")
        return False
