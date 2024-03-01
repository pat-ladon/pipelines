import os
import json
import datetime
import pandas as pd
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
        
    def convert_datetime(self, item):
        """Converts pandas.Timestamp or datetime.date to string format."""
        if isinstance(item, (pd.Timestamp, datetime.date)):
            return item.isoformat()
        return item
        
    def clear_and_update_sheet(self, sheet_name, df):
        # Convert date and Timestamp to string
        for col in df.select_dtypes(include=['datetime64', 'object']).columns:
            df[col] = df[col].apply(self.convert_datetime)
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
        ).execute(num_retries=3)

    def append_to_sheet(self, sheet_name: str, df: pd.DataFrame):
        """Appends new data to a sheet without overwriting existing data."""
        # Convert date and Timestamp to string
        df = df.applymap(self.convert_datetime)
        
        # Convert DataFrame to a list of lists for the append operation
        values = df.values.tolist()
        
        # Append data starting at the first column, automatically finding the first empty row
        self.service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f'{sheet_name}!A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': values}
        ).execute()