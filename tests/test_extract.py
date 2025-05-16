import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import pandas as pd
import re
from utils.extract import fetchContent, extract_collection_fashion, scrape_fashion, scrape
import requests

class TestExtractFunction(unittest.TestCase):
    def setUp(self):
        self.dummy_html = '''
        <div class="collection-card">
            <h3>Cool Jacket</h3>
            <span class="price">$100.00</span>
            <p>Rating: ⭐ 4.5 / 5</p>
            <p>5 Colors</p>
            <p>Size: M</p>
            <p>Gender: Men</p>
        </div>
        '''
        self.soup = BeautifulSoup(self.dummy_html, 'html.parser')
        self.collection = self.soup.find('div', class_='collection-card')

    def test_fetch_content_success(self):
        with patch('utils.extract.requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b'<html></html>'
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            content = fetchContent('http://example.com')
            self.assertIsNotNone(content)
            mock_get.assert_called_once()

    def test_fetch_content_failure(self):
        with patch('utils.extract.requests.Session.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("Error")
            mock_get.return_value = mock_response

            content = fetchContent('http://example.com')
            self.assertIsNone(content)

    def test_extract_collection_fashion(self):
        result = extract_collection_fashion(self.collection)
        self.assertEqual(result['Title'], 'Cool Jacket')
        self.assertEqual(result['Price'], '$100.00')
        self.assertEqual(result['Rating'], '⭐ 4.5 / 5')
        self.assertEqual(result['Colors'], '5 Colors')
        self.assertEqual(result['Size'], 'M')
        self.assertEqual(result['Gender'], 'Men')
        self.assertRegex(result['Timestamp'], r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}')

    @patch('utils.extract.fetchContent')
    def test_scrape_fashion(self, mock_fetch):
        first_page_html = '''
        <div class="collection-card">
            <h3>Cool Jacket</h3>
            <span class="price">$100.00</span>
            <p>Rating: ⭐ 4.5 / 5</p>
            <p>5 Colors</p>
            <p>Size: M</p>
            <p>Gender: Men</p>
        </div>
        '''
        second_page_html = '''
        <div class="collection-card">
            <h3>Denim Pants</h3>
            <span class="price">$75.00</span>
            <p>Rating: ⭐ 4.0 / 5</p>
            <p>3 Colors</p>
            <p>Size: L</p>
            <p>Gender: Women</p>
        </div>
        <li class="next"></li> <!-- Tidak ada <a> berarti stop -->
        '''

        mock_fetch.side_effect = [first_page_html, second_page_html]

        data = scrape_fashion("http://dummy.com", "http://dummy.com/page{}", startPage=2, delay=0)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['Title'], "Cool Jacket")
        self.assertEqual(data[1]['Title'], "Denim Pants")

    @patch('utils.extract.scrape_fashion')
    def test_main_returns_dataframe(self, mock_scrape):
        mock_scrape.return_value = [
            {
                'Title': 'Test',
                'Price': '$1.00',
                'Rating': '⭐ 5',
                'Colors': 'Red',
                'Size': 'S',
                'Gender': 'Unisex',
                'Timestamp': '2025-05-15 12:00:00.123'
            }
        ]
        df = scrape()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.shape[0], 1)
        self.assertIn('Title', df.columns)
        self.assertEqual(df.loc[0, 'Title'], 'Test')

if __name__ == '__main__':
    unittest.main()
