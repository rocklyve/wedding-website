import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_confirmation_email(to_email, subject, body):
    smtp_host = st.secrets["smtp"]["host"]
    smtp_port = st.secrets["smtp"].get("port", 587)
    smtp_user = st.secrets["smtp"]["user"]
    smtp_password = st.secrets["smtp"]["password"]
    from_email = st.secrets["smtp"].get("from", smtp_user)

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Fehler beim Senden der Bestätigungs-E-Mail: {e}")
        return False
