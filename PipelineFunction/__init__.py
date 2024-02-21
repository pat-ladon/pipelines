import azure.functions as func
from dotenv import load_dotenv
#TODO: Remove dotenv
import logging
import pandas as pd
from position_data_processor import PositionDataProcessor  # Adjust import as necessary
from google_sheets_client import GoogleSheetsClient  # Adjust import as necessary

load_dotenv()
logging.Logger.root.level = 10
#TODO: Remove dotenv

def main(myTimer: func.TimerRequest) -> None: # Azure Functions trigger
    
    logging.info(f'Pipeline started | { pd.Timestamp.now()}')
    source_url = 'https://www.fca.org.uk/publication/data/short-positions-daily-update.xls'

    processor = PositionDataProcessor(source_url)
    sheets_client = GoogleSheetsClient()

    # Process positions and get dataframes
    exploded_df, mapping_df = processor.process_positions()

    # Update sheets - Adjust 'Sheet1' and 'Sheet2' to your actual sheet names
    try:
    # Code to update Google Sheet
        sheets_client.clear_and_update_sheet('shortsellerupdate', exploded_df)
        logging.info(f"shortsellerupdate with {exploded_df.shape[0]} rows updated on {pd.Timestamp.now()}")
    except Exception as e:
        print(f"Error updating shortsellerupdate tab: {e}")
    try:
    # Code to update Google Sheet
        sheets_client.clear_and_update_sheet('fundmapping', mapping_df)
        logging.info(f"fundmapping with {mapping_df.shape[0]} rows updated on {pd.Timestamp.now()}")
    except Exception as e:
        print(f"Error updating fundmapping tab: {e}")    

    # Log the update
    logging.info(f"Google Sheets updated with new data on {pd.Timestamp.now()}")