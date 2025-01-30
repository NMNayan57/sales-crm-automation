import gspread
from google.oauth2.service_account import Credentials
import requests

# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Authenticate using Service Account JSON
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

# Open Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YFDMxGkb3tgiwD8rQZdiTnkRDKos_qVrbZXSzZso5h8"
sheet = client.open_by_url(SHEET_URL).sheet1

# Function to simulate sending an email
def send_email(email, lead_name):
    print(f"📧 Sending email to {lead_name} ({email})")  # Debugging Output
    return "Sent"

# Fetch all data
data = sheet.get_all_records()

# Process leads assigned to Agent B
for idx, lead in enumerate(data, start=2):  # Start from row 2 (skip headers)
    email = lead.get("Email", "").strip()  # Ensure email is retrieved safely
    lead_name = lead.get("Lead Name", "").strip()

    if not email or lead.get("Email Verified (Y/N)") != "Y" or lead.get("Response Status"):
        continue  # Skip invalid or already contacted leads

    email_status = send_email(email, lead_name)

    if email_status == "Sent":
        sheet.update_cell(idx, 7, "Contacted")  # Mark as contacted
        print(f"✅ Updated Sheet: {lead_name} marked as Contacted")
    else:
        sheet.update_cell(idx, 7, "Failed")  # Mark as failed
        print(f"❌ Email failed for: {lead_name} ({email})")

print("\n✅ Agent B - Sales Outreach Completed.")
