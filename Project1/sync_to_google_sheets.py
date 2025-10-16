"""
Upload raw Lodasoft data from local CSVs to a shared Google Sheet.

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
import numpy as np
import os

def upload_csv_to_sheet(csv_path, tab_name, sheet_name="Mail_Data_Generation", creds_path="../../credentials.json"):
    try:
        # Authenticate
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        # Open sheet and tab
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(tab_name)

        # Load and clean data
        df = pd.read_csv(csv_path)
        df.replace([np.nan, np.inf, -np.inf], "", inplace=True)
        df = df.applymap(lambda x: str(x).strip())

        # Upload
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        print(f"✅ Uploaded {os.path.basename(csv_path)} to '{tab_name}' tab")

    except Exception as e:
        print(f"❌ Failed to upload {csv_path} to '{tab_name}': {e}")


def import_sheet_tab_to_csv(tab_name, output_filename=None, sheet_name="Mail_Data_Generation", creds_path="../../credentials.json"):
    try:
        # Authenticate
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)

        # Open sheet and tab
        sheet = client.open(sheet_name)
        worksheet = sheet.worksheet(tab_name)

        # Extract and clean data
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])

        # Default output filename if not provided
        if output_filename is None:
            output_filename = f"{tab_name}.csv"

        # Save to CSV in data/processed/
        output_path = os.path.join("..", "..", "data", "processed", output_filename)
        df.to_csv(output_path, index=False)

        print(f"✅ Imported '{tab_name}' tab to {output_path}")
        return df

    except Exception as e:
        print(f"❌ Failed to import '{tab_name}' tab: {e}")
        return None