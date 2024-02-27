import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import os
from dotenv import load_dotenv, find_dotenv


# the url of the home page of the target website
base_url = 'https://www.nintendolife.com/guides/pokemon-scarlet-and-violet-mystery-gift-codes-list'

# defining the User-Agent header to use in the GET request below
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64;'
                  ' x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

page = requests.get(base_url, headers=headers)

soup = BeautifulSoup(page.text, 'html.parser')


load_dotenv(find_dotenv())

uri = os.environ.get('MONGO_URI')
client = MongoClient(uri)
codes_db = client.codes
collection = codes_db.codes


def find_code(criteria):
    return collection.find_one(criteria)


def scrape_page():
    code_elements = soup.find_all('table')
    new_codes = []
    code_rows = code_elements[0].find('tbody').find_all("tr")
    for code_row in code_rows:
        code_tds = code_row.find_all("td")

        details = []
        for code_td in code_tds:
            details.append(code_td.text)

        code = details[0]
        gift = details[1]
        expire_date = details[2]

        existing_code = find_code({"gift": gift})
        if not existing_code:
            new_codes.append(
                {
                    'code': code,
                    'gift': gift,
                    'expire_date': expire_date
                }
            )
    return new_codes
