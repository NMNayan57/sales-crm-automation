import os
import base64
import json
import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email import message_from_string

# Load Gmail Credentials
creds = Credentials.from_authorized_user_file("token.json")

# Connect to Gmail API
service = build("gmail", "v1", credentials=creds)

# Load Google Sheets Credentials
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YFDMxGkb3tgiwD8rQZdiTnkRDKos_qVrbZXSzZso5h8"
gc = gspread.service_account(filename="credentials.json")
sheet = gc.open_by_url(SHEET_URL).sheet1

# Function to extract response status
def get_response_status(email_body):
    email_body = email_body.lower()
    if "interested" in email_body:
        return "Interested"
    elif "not interested" in email_body or "unsubscribe" in email_body:
        return "Not Interested"
    else:
        return "No Response"

# Function to extract email body
def extract_email_body(message):
    if "parts" in message["payload"]:
        for part in message["payload"]["parts"]:
            if part["mimeType"] == "text/plain":
                return base64.urlsafe_b64decode(part["body"].get("data", "")).decode("utf-8", errors="ignore")
    return "No Body Content"

# Function to check emails
def check_email():
    results = service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No new emails.")
        return

    print(f"\n📩 {len(messages)} new emails found!")
    unmatched_responses = []

    for msg in messages:
        msg_id = msg["id"]
        message = service.users().messages().get(userId="me", id=msg_id).execute()

        # Extract subject
        subject = next(
            (header["value"] for header in message["payload"]["headers"] if header["name"] == "Subject"), "No Subject"
        )

        # Ignore bounce-back failure emails
        if "Delivery Status Notification" in subject or "failure" in subject.lower():
            print("🚨 Skipping bounce-back email...")
            continue

        # Extract sender email
        sender_email = next(
            (header["value"] for header in message["payload"]["headers"] if header["name"] == "From"), "Unknown"
        )

        # Extract email body
        email_body = extract_email_body(message)
        response_status = get_response_status(email_body)

        print(f"📧 Response from {sender_email} - Subject: {subject} - Status: {response_status}")

        # Update response in Google Sheets
        updated = update_google_sheet(sender_email, response_status)
        if not updated:
            unmatched_responses.append(f"{sender_email}: {response_status}")

    # Log unmatched responses
    if unmatched_responses:
        with open("unmatched_responses.log", "a") as log_file:
            log_file.write("\n".join(unmatched_responses) + "\n")
        print("⚠️ Some responses could not be matched. Logged in unmatched_responses.log")

# Function to update Google Sheet
def update_google_sheet(sender_email, response_status):
    data = sheet.get_all_records()
    
    for idx, lead in enumerate(data, start=2):  # Start from row 2 (skip headers)
        if lead.get("Email") == sender_email:
            current_status = lead.get("Response Status", "")
            if current_status != response_status:  # Avoid overwriting valid responses
                sheet.update_cell(idx, 7, response_status)
                print(f"✅ Updated response for {sender_email}: {response_status}")
            else:
                print(f"ℹ️ Response for {sender_email} is already up to date.")
            return True
    return False

# Run the email check
check_email()
