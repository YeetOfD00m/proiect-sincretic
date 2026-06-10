import smtplib
import ssl
from getpass import getpass
from email.message import EmailMessage

port = 465
smtp_server = "smtp.gmail.com"
sender_email = "psnproiect@gmail.com"
receiver_email = "bogdantatomir21@gmail.com"
password = "nnvaqibhqqjnnxkd"

def send(msg, sender_email="psnproiect@gmail.com", debug=True):
    if debug:
        smtp_server = "localhost"
        port = 8025
        with smtplib.SMTP(smtp_server, port) as server:
            server.send_message(msg)

    else:
        port = 465
        smtp_server = "smtp.gmail.com"
        password = "nnva qibh qqjn nxkd"
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            smtp_server, port, context=context
        ) as server:
            server.login(sender_email, password)
            server.send_message(build_email(msg))

# Build Email Message
def build_email(event):
    msg = EmailMessage()
    msg["to"] = receiver_email
    msg["from"] = sender_email
    msg["subject"] = "Alerta INUNDATIE!"
    msg.set_content(f"""
                ALERTĂ INUNDAȚIE!
                
                Timp: {event['timestamp']}
                Mesaj: {event['message']}
                
                Vă rugăm să verificați sistemul imediat.

                """)
    return msg