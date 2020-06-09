import requests
from bs4 import BeautifulSoup
import pickle
import datetime
import re
from datetime import datetime


def get_list_of_desired_currencies():
    return


def download_coin_to_pickle(coin, end_date):
    """downloads the content online from CMC and saves to pickle file"""
    page_get = requests.get('https://coinmarketcap.com/currencies/' + coin +
                            '/historical-data/?start=20110428&end=' + end_date)
    pickle_name = str(coin) + str('_page_pickle')
    outfile = open(pickle_name, 'wb')
    pickle.dump(page_get, outfile)
    outfile.close()


def load_coin_pickle_to_object(coin):
    """load content from saved pickle file"""
    pickle_name = str(coin) + str('_page_pickle')
    infile = open(pickle_name, 'rb')
    page_get = pickle.load(infile)
    infile.close()
    return page_get


def update_coins_data(currencies_to_update):
    """updates the database of pickle file for the currencies provided"""
    current_day = str(datetime.now().strftime("%Y%m%d"))
    [download_coin_to_pickle(coin, current_day) for coin in currencies_to_update]


def experiments():
    """this is a general function where we can try out anything.."""

    # load file from file directory rather then online - saves time for our project's purposes
    page = load_coin_pickle_to_object('bitcoin')
    print(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup.prettify())
    # (soup.prettify())
    date_dirty = soup.find_all(class_="cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")
    test_dirty = str(date_dirty[1])
    print(test_dirty)
    end = test_dirty.index('</div></td>')
    test_clean = test_dirty[end - 12:end]
    print(test_clean)
    date_time_obj = datetime.strptime(test_clean, '%b %d, %Y').date()
    print(date_time_obj)


if __name__ == '__main__':
    """use this command to update the pickle files we use"""
    # update_coins_data(['bitcoin', 'ethereum'])
    experiments()


