import requests
from bs4 import BeautifulSoup
from datetime import datetime


def update_database():
    return


def get_list_of_desired_currencies():
    return



page = requests.get('https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20110428&end=20200606')
print(page)
soup = BeautifulSoup(page.content, 'html.parser')
print(soup.prettify())
(soup.prettify())