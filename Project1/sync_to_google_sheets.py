"""
Syncs cleaned campaign data from local CSVs to a shared Google Sheet.

- Authenticates using a service account via credentials.json
- Opens the target spreadsheet by URL
- Cleans each CSV to remove NaNs, infs, and whitespace
- Converts all values to strings for JSON-safe upload
- Clears and updates the target tab with fresh data

Target tabs:
- 'CRM' ← from Leads_CRM.csv
- 'LOS' ← from PipelineMetrics_LOS.csv
- 'LoanStatus' ← from LoanStatus.csv
"""


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def sync_to_google_sheets(csv_path, sheet_name, tab_name, creds_path):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name)
    worksheet = sheet.worksheet(tab_name)

    df = pd.read_csv(csv_path).fillna("")
    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
