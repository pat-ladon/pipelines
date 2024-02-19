from dotenv import load_dotenv
#TODO: Remove dotenv
import logging
from .position_data_processor import PositionDataProcessor  # Adjust import as necessary
from .google_sheets_client import GoogleSheetsClient  # Adjust import as necessary

load_dotenv()
#TODO: Remove dotenv

def main(name: str) -> None:  # Azure Functions trigger
    source_url = 'https://www.fca.org.uk/publication/data/short-positions-daily-update.xls'
    spreadsheet_id = 'your_spreadsheet_id_here'
    credentials_file = 'path/to/your/credentials.json'

    processor = PositionDataProcessor(source_url)
    sheets_client = GoogleSheetsClient(credentials_file, spreadsheet_id)

    # Process positions and get dataframes
    exploded_df, mapping_df = processor.process_positions()

    # Update sheets - Adjust 'Sheet1' and 'Sheet2' to your actual sheet names
    sheets_client.update_sheet('shortsellerupdate', exploded_df)
    sheets_client.update_sheet('fundmapping', mapping_df)

    # Log the update
    logging.info(f"Google Sheets updated with new data on {pd.Timestamp.now()}")