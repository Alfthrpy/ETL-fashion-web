import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.load import save_to_csv, save_to_postgres, save_to_spreadsheet


class TestLoadFunctions(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame({
            'Name': ['Item 1', 'Item 2'],
            'Price': [10.5, 20.0]
        })
        self.fake_path = "tests/"
        self.fake_filename = "output.csv"
        self.fake_db_url = "postgresql://user:pass@localhost/dbname"
        self.spreadsheet_id = "dummy_spreadsheet_id"
        self.client_secret_path = "dummy_client_secret.json"
        self.range_name = "Sheet1!A1:B2"

    @patch("builtins.open", new_callable=mock_open)
    @patch("pandas.DataFrame.to_csv")
    def test_save_to_csv_success(self, mock_to_csv, mock_open_file):
        save_to_csv(self.df, self.fake_filename, self.fake_path)
        mock_to_csv.assert_called_once()

    @patch("pandas.DataFrame.to_sql")
    @patch("utils.load.create_engine")
    def test_save_to_postgres_success(self, mock_create_engine, mock_to_sql):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_conn = mock_engine.connect.return_value.__enter__.return_value

        save_to_postgres(self.df, self.fake_db_url)
        mock_to_sql.assert_called_once_with('fashionproducts', con=mock_conn, if_exists='append', index=False)

    @patch("utils.load.Credentials.from_service_account_file")
    @patch("utils.load.build")
    def test_save_to_spreadsheet_success(self, mock_build, mock_creds):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_sheet = mock_service.spreadsheets.return_value
        mock_sheet.values.return_value.update.return_value.execute.return_value = {}

        save_to_spreadsheet(self.df, self.spreadsheet_id, self.client_secret_path, self.range_name)
        mock_sheet.values.return_value.update.assert_called_once()

    @patch("pandas.DataFrame.to_csv", side_effect=Exception("Write error"))
    def test_save_to_csv_failure(self, mock_to_csv):
        with self.assertLogs(level='ERROR') as cm:
            save_to_csv(self.df, self.fake_filename, self.fake_path)
            self.assertIn("error save to csv", cm.output[0])

    @patch("pandas.DataFrame.to_sql", side_effect=Exception("DB error"))
    @patch("utils.load.create_engine")
    def test_save_to_postgres_failure(self, mock_create_engine, mock_to_sql):
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        with self.assertLogs(level='ERROR'):
            save_to_postgres(self.df, self.fake_db_url)

    @patch("utils.load.build", side_effect=Exception("Google API error"))
    @patch("utils.load.Credentials.from_service_account_file")
    def test_save_to_spreadsheet_failure(self, mock_creds, mock_build):
        with self.assertLogs(level='ERROR') as cm:
            save_to_spreadsheet(self.df, self.spreadsheet_id, self.client_secret_path, self.range_name)
            self.assertIn("error save to spreadsheets", cm.output[0])


if __name__ == '__main__':
    unittest.main()
