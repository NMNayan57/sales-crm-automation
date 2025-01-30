from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send"
]

flow = InstalledAppFlow.from_client_secrets_file("gmail_credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

# Save new token
with open("token.json", "w") as token:
    token.write(creds.to_json())

print("✅ Authentication successful! New token saved.")
