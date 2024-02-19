import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleSheetsClient:
    def __init__(self, spreadsheet_id):
        self.credentials = self.authenticate()
        self.spreadsheet_id = spreadsheet_id

    def authenticate(self):
        # Load credentials from environment variables
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        credentials = Credentials.from_service_account_info(json.loads(creds_json))
        service = build('sheets', 'v4', credentials=credentials)
        return service
        
    def update_sheet(self, sheet_name, df):
            # Convert df to a list of lists
            values = df.values.tolist()
            # Include headers
            values.insert(0, df.columns.tolist())
            # Specify the range to update, e.g., 'Sheet1' or 'A1'
            range_name = f'{sheet_name}!A1'
            # Use the Sheets API to update the sheet
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=range_name,
                valueInputOption='USER_ENTERED', body={'values': values}).execute()