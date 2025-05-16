import pandas as pd
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging
from sqlalchemy import create_engine

# Configure logging
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "load.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

def save_to_csv(df: pd.DataFrame, filename: str, path: str):
    '''Menyimpan dataframe ke csv'''
    try:
        full_path = os.path.join(path, filename)
        df.to_csv(full_path, index=False)
        logging.info("save to csv success")
    except Exception as e:
        logging.error(f"error save to csv : {e}")


def save_to_spreadsheet(df: pd.DataFrame, spreadsheet_id: str, client_secret_path: str, range_name: str):
    '''Menyimpan dataframe ke spreadsheet'''

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    try:
        credentials = Credentials.from_service_account_file(client_secret_path, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # Convert DataFrame to list of lists, ensuring all values are JSON serializable
        df_serializable = df.map(lambda x: x.isoformat() if hasattr(x, 'isoformat') else x)
        values = df_serializable.values.tolist()

        body = {
            'values': values
        }

        result = sheet.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        logging.info("save to spreadsheets success")
    except Exception as e:
        logging.error(f"error save to spreadsheets : {e}")


def save_to_postgres(data:pd.DataFrame,db_url:str):
    """Fungsi untuk menyimpan data ke dalam PostgreSQL."""
    try:
        # Membuat engine database
        engine = create_engine(db_url)
        
        # Menyimpan data ke tabel 'bookstoscrape' jika tabel sudah ada, data akan ditambahkan (append)
        with engine.connect() as con:
            data.to_sql('fashionproducts', con=con, if_exists='append', index=False)
            logging.info("save to postgres success")
    
    except Exception as e:
        logging.error(f"error save to postgres: {e}")