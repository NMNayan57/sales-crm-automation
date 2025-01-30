import gspread
from google.oauth2.service_account import Credentials

# Define the scope for Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Authenticate using Service Account JSON
creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
client = gspread.authorize(creds)

# Open Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YFDMxGkb3tgiwD8rQZdiTnkRDKos_qVrbZXSzZso5h8"
sheet = client.open_by_url(SHEET_URL).sheet1

# Fetch all data
data = sheet.get_all_records()

# Count total leads
total_leads = sum(1 for lead in data if lead.get("Email", "").strip())

# Count verified leads
verified_count = sum(1 for lead in data if lead.get("Email Verified (Y/N)") == "Y")

# Count leads contacted
leads_contacted = sum(1 for lead in data if lead.get("Response Status") == "Contacted")

# Calculate leads not contacted (Total Leads - Leads Contacted)
leads_not_contacted = total_leads - leads_contacted

# Count interested and not interested leads based on responses
interested_count = sum(1 for lead in data if lead.get("Response Status") == "Interested")
not_interested_count = sum(1 for lead in data if lead.get("Response Status") == "Not Interested")

# Mark verified but uncontacted leads as "Not Contacted"
for idx, lead in enumerate(data, start=2):
    if lead.get("Email Verified (Y/N)") == "Y" and not lead.get("Response Status"):
        sheet.update_cell(idx, 7, "Not Contacted")  # Column G (Response Status)

# Print campaign summary
print("\n✅ Supervisor Summary:")
print(f"📌 Total Leads: {total_leads}")
print(f"📌 Verified Leads: {verified_count}")
print(f"📌 Leads Contacted: {leads_contacted}")
print(f"📌 Leads Not Contacted: {leads_not_contacted}")
print(f"📌 Interested Leads: {interested_count}")
print(f"📌 Not Interested Leads: {not_interested_count}")

# Write summary back to Google Sheet
sheet.update_cell(1, 8, "Summary")
sheet.update_cell(2, 8, f"Total Leads: {total_leads}")
sheet.update_cell(3, 8, f"Verified Leads: {verified_count}")
sheet.update_cell(4, 8, f"Leads Contacted: {leads_contacted}")
sheet.update_cell(5, 8, f"Leads Not Contacted: {leads_not_contacted}")
sheet.update_cell(6, 8, f"Interested Leads: {interested_count}")
sheet.update_cell(7, 8, f"Not Interested Leads: {not_interested_count}")
