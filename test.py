import requests
from bs4 import BeautifulSoup
import datetime
import re
from datetime import datetime


def update_database():
    return


def get_list_of_desired_currencies():
    return


page = requests.get('https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20110428&end=20200606')
print(page)
soup = BeautifulSoup(page.content, 'html.parser')
# print(soup.prettify())
# (soup.prettify())
date_dirty = soup.find_all(class_="cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")
test_dirty = str(date_dirty[1])
print(test_dirty)
end = test_dirty.index('</div></td>')
test_clean = test_dirty [end-12:end]
print(test_clean)
date_time_obj = datetime.strptime(test_clean, '%b %d, %Y').date()
print(date_time_obj)

