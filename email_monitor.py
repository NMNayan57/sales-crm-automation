import base64
import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 🔹 Load Credentials
GMAIL_TOKEN = "token.json"
SHEET_CREDENTIALS = "credentials.json"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YFDMxGkb3tgiwD8rQZdiTnkRDKos_qVrbZXSzZso5h8"

# 🔹 Authenticate with Gmail & Google Sheets
gmail_service = build("gmail", "v1", credentials=Credentials.from_authorized_user_file(GMAIL_TOKEN))
gc = gspread.service_account(filename=SHEET_CREDENTIALS)
sheet = gc.open_by_url(SHEET_URL).sheet1  # First sheet

# 🔹 Function to determine response status
def get_response_status(email_body):
    email_body = email_body.lower()
    if "interested" in email_body:
        return "Interested"
    elif "not interested" in email_body or "unsubscribe" in email_body:
        return "Not Interested"
    return "No Response"

# 🔹 Function to fetch & process emails
def check_email():
    results = gmail_service.users().messages().list(userId="me", maxResults=10).execute()
    messages = results.get("messages", [])

    if not messages:
        print("📭 No new emails found.")
        return

    print(f"📩 {len(messages)} new emails found!")

    for msg in messages:
        msg_id = msg["id"]
        message = gmail_service.users().messages().get(userId="me", id=msg_id).execute()

        # 🔹 Extract sender email & subject
        headers = message["payload"]["headers"]
        sender_email = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")

        # 🔹 Skip bounce-back failure emails
        if "Delivery Status Notification" in subject.lower() or "failure" in subject.lower():
            print("🚨 Skipping bounce-back email...")
            continue

        # 🔹 Extract email body
        email_body = base64.urlsafe_b64decode(
            message["payload"]["parts"][0]["body"].get("data", "")
        ).decode("utf-8", errors="ignore") if "parts" in message["payload"] else "No Body Content"

        response_status = get_response_status(email_body)
        print(f"📧 New Email from {sender_email} - Subject: {subject} - Response: {response_status}")

        # 🔹 Update response in Google Sheets
        update_google_sheet(sender_email, response_status)

# 🔹 Function to update Google Sheets
def update_google_sheet(sender_email, response_status):
    data = sheet.get_all_records()
    
    for idx, lead in enumerate(data, start=2):  # Start from row 2 (skip headers)
        if lead.get("Email") == sender_email:
            sheet.update_cell(idx, 7, response_status)  # Column G: "Response Status"
            print(f"✅ Updated response for {sender_email}: {response_status}")
            return

    # 🔹 Auto-add new lead if not found
    print(f"⚠️ No matching lead found for {sender_email}. Adding to the sheet.")
    sheet.append_row([sender_email, "", "", "", "", "N", response_status])

# 🔹 Run the email check
check_email()
