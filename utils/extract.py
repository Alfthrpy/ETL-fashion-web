import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
import re
import string
import logging
from datetime import datetime
import os

# Configure logging
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(log_dir, exist_ok=True)
log_file_path = os.path.join(log_dir, "scraping.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetchContent(url: string):
    '''Mengambil konten html dari url yang diberikan'''
    session = requests.Session()
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching content from URL {url}: {e}")
        return None

def extract_collection_fashion(collection: Tag):
    '''Mengambil data fashion berupa title, price, rating, colors, size, gender dari collection'''
    title = collection.find('h3').text.strip()
    price_tag = collection.find('span', class_='price')
    price = price_tag.text.strip() if price_tag else None

    p_tags = collection.find_all('p')
    if price == None:
        p_tags.pop(0)

    values = []
    for p in p_tags:
        text = p.get_text(strip=True)
        cleaned = re.sub(r'^(Rating|Size|Gender):\s*', '', text)
        values.append(cleaned)

    fashion = {
        'Title': title,
        'Price': price,
        'Rating': values[0] if len(values) > 0 else None,
        'Colors': values[1] if len(values) > 1 else None,
        'Size': values[2] if len(values) > 2 else None,
        'Gender': values[3] if len(values) > 3 else None,
        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    }

    return fashion

def scrape_fashion(baseUrl: string, paginationUrl: string, startPage=2, delay=1):
    '''Fungsi utama untuk mengambil keseluruhan data, mulai dari requests hingga menyimpan ke variabel data'''
    logging.info("Starting scraping process")
    data = []
    pageNumber = startPage
    firstPage = True

    while True:
        if firstPage:
            logging.info("Scraping first page")
            content = fetchContent(baseUrl)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                collectionElements = soup.find_all('div', class_='collection-card')
                for collection in collectionElements:
                    fashion = extract_collection_fashion(collection)
                    data.append(fashion)
                firstPage = False
        else:
            url = paginationUrl.format(pageNumber)
            logging.info(f"Scraping page {pageNumber}")
            content = fetchContent(url)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                collectionElements = soup.find_all('div', class_='collection-card')
                for collection in collectionElements:
                    fashion = extract_collection_fashion(collection)
                    data.append(fashion)

            next_button = soup.find('li', class_='next')
            if next_button and next_button.find('a'):  # <a> hanya ada kalau masih bisa lanjut
                pageNumber += 1
                time.sleep(delay)
            else:
                logging.info("No more pages to scrape")
                break
            
    logging.info("Scraping process completed")
    return data

def scrape():
    '''Fungsi utama untuk keseluruhan proses scraping'''
    logging.info("Starting main function")
    BASE_URL = "https://fashion-studio.dicoding.dev/"
    PAGINATION_URL = "https://fashion-studio.dicoding.dev/page{}"

    all_fashion_data = scrape_fashion(BASE_URL, PAGINATION_URL,startPage=2,delay=0)
    df = pd.DataFrame(all_fashion_data)

    return df

