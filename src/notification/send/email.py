import json
import os
import smtplib
from email.message import EmailMessage


def notification(message):
    try:
        message = json.loads(message)
        mp3_fid = message["mp3_fid"]
        sender_address = os.environ.get["GMAIL_ADDRESS"]
        sender_password = os.environ.get["GMAIL_PASSWORD"]
        receiver_address = message["username"]

        msg = EmailMessage()
        msg.set_content(f"mp3 file_id: {mp3_fid} is now ready!")
        msg["Subject"] = "mp3 file ready"
        msg["From"] = sender_address
        msg["To"] = receiver_address

        with smtplib.SMTP("smtp.gmail.com", 587) as session:
            session.starttls()
            session.login(sender_address, sender_password)
            session.send_message(msg)

        print("email sent!")
    except Exception as error:
        print(error)
        return error
