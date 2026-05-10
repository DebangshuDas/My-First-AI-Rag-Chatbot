import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(mail_data):

    try:

        sender_email = os.getenv("EMAIL_ADDRESS")
        sender_password = os.getenv("EMAIL_PASSWORD")

        msg = MIMEMultipart()

        msg["From"] = sender_email # type: ignore
        msg["To"] = mail_data["to"]
        msg["Subject"] = mail_data["subject"]

        if mail_data["cc"]:
            msg["Cc"] = mail_data["cc"]

        msg.attach(
            MIMEText(mail_data["body"], "plain")
        )

        recipients = [mail_data["to"]]

        if mail_data["cc"]:
            recipients.append(mail_data["cc"])

        if mail_data["bcc"]:
            recipients.append(mail_data["bcc"])

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        server.login(
            sender_email, # type: ignore # type: ignore 
            sender_password # type: ignore
        )

        server.sendmail(
            sender_email, # type: ignore
            recipients,
            msg.as_string()
        )

        server.quit()

        return "Email sent successfully."

    except Exception as e:

        return f"Email sending failed: {str(e)}"