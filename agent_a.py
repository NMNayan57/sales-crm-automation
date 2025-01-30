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

# Hunter.io API Key (Replace with a valid API key)
HUNTER_API_KEY = "d5e21f7edadecc1baf7a8f92e4568e7ee78054ac"

# Function to verify email using Hunter.io
def verify_email(email):
    if not email:  # Skip blank emails
        return "unknown"
    
    response = requests.get(f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}")
    print(f"🔍 Checking {email}: {response.text}")  # Debugging output

    if response.status_code == 200:
        result = response.json()
        return result.get("data", {}).get("status", "unknown")  # "valid" means email is good
    
    return "unknown"

# Fetch all data
data = sheet.get_all_records()

# Process leads assigned to Agent A
for idx, lead in enumerate(data, start=2):  # Start from row 2 (skip headers)
    email = lead.get("Email", "").strip()  # Ensure email is retrieved safely

    if not email or lead.get("Email Verified (Y/N)"):  # Skip blank or already verified
        continue  

    verification_result = verify_email(email)

    if verification_result == "valid":
        sheet.update_cell(idx, 6, "Y")  # Mark as verified
        print(f"✅ Verified: {lead['Lead Name']} ({email})")
    else:
        sheet.update_cell(idx, 6, "N")  # Mark as not verified
        print(f"❌ Invalid: {lead['Lead Name']} ({email})")

print("\n✅ Agent A - Email Verification Completed.")
