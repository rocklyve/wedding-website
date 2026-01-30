import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "mxf9a8.netcup.net"
SMTP_PORT = 587
SMTP_USER = "david@laubenstein.net"
SMTP_PASSWORD = ""
FROM_EMAIL = SMTP_USER
TO_EMAIL = SMTP_USER

msg = MIMEText("SMTP Testmail aus dem LXC", "plain", "utf-8")
msg["Subject"] = "SMTP Test"
msg["From"] = FROM_EMAIL
msg["To"] = TO_EMAIL

try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
    server.quit()
    print("Testmail erfolgreich gesendet")
except Exception as e:
    print("Fehler:", e)