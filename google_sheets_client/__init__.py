import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class GoogleSheetsClient:
    def __init__(self):
        self.credentials = self.authenticate()
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID")
        self.service = self.authenticate()

    def authenticate(self):
        # Load credentials from environment variables
        creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
        credentials = Credentials.from_service_account_info(json.loads(creds_json))
        service = build('sheets', 'v4', credentials=credentials)
        return service
        
    def clear_and_update_sheet(self, sheet_name, df):
        # Clear the entire sheet
        self.service.spreadsheets().values().clear(
            spreadsheetId=self.spreadsheet_id, 
            range=f'{sheet_name}',
        ).execute()
        
        # Convert DataFrame to a list of lists for the update
        values = [df.columns.tolist()] + df.values.tolist()
        
        # Update starting at A1, automatically adjusting the range to fit new data
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id, 
            range=f'{sheet_name}!A1',
            valueInputOption='USER_ENTERED', 
            body={'values': values}
        ).execute()