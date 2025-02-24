import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Google API Authentication
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "your-service-account.json", scope
)
client = gspread.authorize(creds)

# Open the Google Sheet
sheet = client.open("Your Google Sheet Name").sheet1

# Load CSV into DataFrame
df = pd.read_csv("hotel_data.csv")

# Convert DataFrame to List of Lists
data = [df.columns.tolist()] + df.values.tolist()

# Upload to Google Sheets
sheet.update("A1", data)

print("✅ Data uploaded successfully!")
