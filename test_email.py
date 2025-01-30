from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText

# Load credentials from token.json
creds = Credentials.from_authorized_user_file("token.json")

# Build the Gmail service
service = build("gmail", "v1", credentials=creds)

def send_email():
    sender_email = "smnoyan670@gmail.com"  # Replace with your email
    recipient_email = "nayan@programming-hero.com"  # Replace with recipient's email
    subject = "Test Email from Python Script"
    body = "Hello! This is a test email sent from the Gmail API using Python."

    message = MIMEText(body)
    message["to"] = recipient_email
    message["from"] = sender_email
    message["subject"] = subject

    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        message = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")

# Run the email send function
send_email()
