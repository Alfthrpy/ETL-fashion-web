import unittest
import pandas as pd
from utils.transform import transform_data

class TestTransformFunction(unittest.TestCase):

    def setUp(self):
        self.exchange_rate = 16000
        self.raw_data = pd.DataFrame({
            'Title': ['Unknown Product', 'Legit Product'],
            'Rating': ['⭐ Invalid Rating / 5', '⭐ 4.5 / 5'],
            'Price': ['Price Unavailable', '$12.99'],
            'Colors': ['3 colors', '5 colors'],
            'Size': ['L', 'M'],
            'Gender': ['Men', 'Women'],
            'Timestamp': ['2024-01-01', 'invalid date']
        })

    def test_transform_valid_data(self):
        df = transform_data(self.raw_data.copy(), self.exchange_rate)

        # hanya 1 row valid harusnya tersisa
        self.assertEqual(len(df), 1)

        # kolom sudah transform
        self.assertIn('Price_in_dolar', df.columns)
        self.assertIn('Price_in_rupiah', df.columns)
        self.assertNotIn('Price', df.columns)

        # isi kolom
        self.assertAlmostEqual(df.iloc[0]['Price_in_dolar'], 12.99, places=2)
        self.assertAlmostEqual(df.iloc[0]['Price_in_rupiah'], 12.99 * self.exchange_rate, places=2)
        self.assertEqual(df.iloc[0]['Colors'], 5)
        self.assertEqual(df.iloc[0]['Rating'], 4.5)

    def test_transform_with_all_invalid(self):
        # Semua baris akan dianggap dirty dan drop
        dirty_df = pd.DataFrame({
            'Title': ['Unknown Product'],
            'Rating': ['Not Rated'],
            'Price': ['Price Unavailable'],
            'Colors': ['no color info'],
            'Size': ['XL'],
            'Gender': ['Unisex'],
            'Timestamp': ['broken date']
        })
        df = transform_data(dirty_df, self.exchange_rate)
        self.assertEqual(len(df), 0)

    def test_transform_handles_missing_columns(self):
        # Kolom Rating & Price tidak ada
        missing_col_df = pd.DataFrame({
            'Title': ['Legit Product'],
            'Colors': ['2 colors'],
            'Size': ['M'],
            'Gender': ['Men'],
            'Timestamp': ['2024-04-01']
        })

        df = transform_data(missing_col_df.copy(), self.exchange_rate)
        self.assertEqual(df is not None, True)
        self.assertEqual(len(df), 1)

    def test_transform_invalid_price_format(self):
        # Price salah format tapi tetap valid barisnya
        df = pd.DataFrame({
            'Title': ['Valid Product'],
            'Rating': ['⭐ 3.0 / 5'],
            'Price': ['InvalidPriceText'],
            'Colors': ['1 colors'],
            'Size': ['S'],
            'Gender': ['Men'],
            'Timestamp': ['2024-04-01']
        })

        result = transform_data(df.copy(), self.exchange_rate)
        self.assertEqual(result['Price_in_dolar'].iloc[0], 0)

    def test_transform_invalid_timestamp(self):
        df = pd.DataFrame({
            'Title': ['Valid Product'],
            'Rating': ['⭐ 3.0 / 5'],
            'Price': ['$10.00'],
            'Colors': ['2 colors'],
            'Size': ['S'],
            'Gender': ['Men'],
            'Timestamp': ['invalid']
        })

        result = transform_data(df.copy(), self.exchange_rate)
        self.assertTrue(pd.isnull(result['Timestamp'].iloc[0]))

if __name__ == '__main__':
    unittest.main()
