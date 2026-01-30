import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

# SMTP-Zugangsdaten (hier eintragen!)
SMTP_HOST = "mxf9a8.netcup.net"
SMTP_PORT = 465
SMTP_USER = "david@laubenstein.net"
SMTP_PASSWORD = ""
FROM_EMAIL = "david@laubenstein.net"
TO_EMAIL = "david@laubenstein.net"  # Testweise an dich selbst

subject = "SMTP Testmail von Python"
body = "Dies ist eine Testmail vom Netcup SMTP-Server.\n\nWenn du diese Mail siehst, funktioniert der Versand!"

msg = MIMEMultipart()
msg["From"] = FROM_EMAIL
msg["To"] = TO_EMAIL
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain", "utf-8"))

def smtp_ssl_ipv4(host, port):
    # Erzwinge IPv4
    addr = socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM)[0][4]
    sock = socket.create_connection(addr)
    return smtplib.SMTP_SSL(host=None, port=None, local_hostname=None, timeout=10, source_address=None, sock=sock)

try:
    with smtp_ssl_ipv4(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
    print("Testmail erfolgreich gesendet!")
except Exception as e:
    print(f"Fehler beim Senden der Testmail: {e}")
