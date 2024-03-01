import pandas as pd
import requests
from typing import Tuple, Dict
from io import BytesIO
from datetime import timedelta

class PositionDataProcessor:
    def __init__(self, source_url: str):
        self.source_url = source_url

    def download_excel(self) -> BytesIO:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(self.source_url, headers=headers)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            raise Exception(f"Failed to download the file: HTTP {response.status_code}")

    def load_sheet(self, keyword: str) -> pd.DataFrame:
        excel_file = self.download_excel()
        xls = pd.ExcelFile(excel_file)
        sheet_name = next((sheet for sheet in xls.sheet_names if keyword.lower() in sheet.lower()), None)
        if sheet_name:
            return pd.read_excel(excel_file, sheet_name=sheet_name)
        return pd.DataFrame()

    @staticmethod
    def filter_recent_records(df: pd.DataFrame, months: int = 6) -> pd.DataFrame:
        df['Position Date'] = pd.to_datetime(df['Position Date'])
        cutoff_date = (pd.Timestamp.today() - pd.DateOffset(months=months))
        return df[df['Position Date'] >= cutoff_date]

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        return df.loc[:, ~df.columns.str.contains('^Unnamed')]

    @staticmethod
    def calculate_next_position_date(df: pd.DataFrame) -> pd.DataFrame:
        df.sort_values(by='Position Date', inplace=True)
        df['Next Position Date'] = df.groupby(['Position Holder', 'Name of Share Issuer'])['Position Date'].shift(-1).fillna(pd.Timestamp('today').date())
        df['Next Position Date'] = df['Next Position Date'].apply(lambda x: x.date() if isinstance(x, pd.Timestamp) else x)
        return df

    @staticmethod
    def apply_date_range(df: pd.DataFrame) -> pd.DataFrame:
        def adjust_date_range(row):
            if row['Net Short Position (%)'] < 0.5:
                return [row['Position Date']]
            else:
                end_date = row['Next Position Date'] - timedelta(days=1)
                return pd.date_range(start=row['Position Date'], end=end_date).date.tolist()
        df['Date Range'] = df.apply(adjust_date_range, axis=1)
        return df

    @staticmethod
    def explode_date_ranges(df: pd.DataFrame) -> pd.DataFrame:
        df_exploded = df.explode('Date Range')
        df_exploded.rename(columns={'Date Range': 'Date'}, inplace=True)
        df_exploded['Date'] = pd.to_datetime(df_exploded['Date']).dt.date  # Ensure date format is correct
        return df_exploded
   
    def anonymize_position_holders(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Anonymize position holder names with a sequence like 'Fund 001', 'Fund 002', etc.
        Returns the DataFrame with anonymized names and a mapping DataFrame.
        """
        df = df.copy()
        unique_holders = df['Position Holder'].unique()
        fund_names = [f"Fund {str(i+1).zfill(3)}" for i in range(len(unique_holders))]
        mapping_dict = dict(zip(unique_holders, fund_names))
        
        df['Position Holder'] = df['Position Holder'].map(mapping_dict)
        
        mapping_df = pd.DataFrame(list(mapping_dict.items()), columns=['Original Name', 'Anonymized Name'])
        
        return df, mapping_df

    def process_positions(self, months: int = 6) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_historic = self.load_sheet("historic")
        df_historic_filtered = self.filter_recent_records(df_historic)
        df_historic_cleaned = self.clean_dataframe(df_historic_filtered)
        
        df_current = self.load_sheet("current")
        df_current_cleaned = self.clean_dataframe(df_current)
        
        final_df = pd.concat([df_historic_cleaned, df_current_cleaned], ignore_index=True)
        
        final_df_with_dates = self.calculate_next_position_date(final_df)
        final_df_with_date_range = self.apply_date_range(final_df_with_dates)
        
        exploded_df = self.explode_date_ranges(final_df_with_date_range)

        exploded_df['Date'] = pd.to_datetime(exploded_df['Date'])
        cutoff_date = pd.Timestamp.today() - pd.DateOffset(months=months)
        filtered_exploded_df = exploded_df[exploded_df['Date'] >= cutoff_date]
        
        # Anonymize position holder names and get the mapping
        anonymized_df, mapping_df = self.anonymize_position_holders(filtered_exploded_df)
        
        return anonymized_df, mapping_df

# # Usage example
# processor = PositionDataProcessor('https://www.fca.org.uk/publication/data/short-positions-daily-update.xls')
# exploded_final_df, mapping_df = processor.process_positions()

# # Optionally, save to CSV
# exploded_final_df.to_csv('anonymized_exploded_final_df.csv', index=False)
# mapping_df.to_csv('position_holder_mapping.csv', index=False)

# print("Processing complete. The DataFrame has been exploded and saved.")
