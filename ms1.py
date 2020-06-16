import requests
from bs4 import BeautifulSoup
import pickle
import datetime
from datetime import datetime
import pandas as pd
import re
from pathlib import Path
from yuval_games import what
MOST_TRADED_CRYPTOS = 'https://trading-education.com/top-100-cryptocurrencies-on-coinmarketcap-in-one-sentence'


############################
# methods dedicated for downloading data and prepare it for analysis
def get_100_currencies():
    page_get = requests.get(MOST_TRADED_CRYPTOS)
    soup = BeautifulSoup(page_get.content, 'html.parser')
    filtered = soup.find_all('h3')
    curr = {}
    for i in map(lambda x: x if x.text[0].isdigit() else None, filtered):
        try:
            er = i.text.split()
            curr.update({' '.join(er[1:-1]): er[-1]})
        except:
            pass
    return curr


def download_coin_data(coin, end_date):
    """downloads the content online from CMC and saves to pickle file"""
    page_get = requests
    html = 'https://coinmarketcap.com/currencies/' + coin.lower() + '/historical-data/?start=20110428&end=' + end_date
    try:
        page_get = requests.get(html)
        Path("pickles\\").mkdir(parents=True, exist_ok=True)
        pickle_name = 'pickles\\' + str(coin)
        print(pickle_name)
        outfile = open(pickle_name, 'wb')
        pickle.dump(page_get, outfile)
        outfile.close()
    except:
        print('error locating', coin, 'data. check possible name mismatch on CMC')


def update_all_coins_data(currencies_to_update):
    """updates the database of pickle file for the currencies provided"""
    current_day = str(datetime.now().strftime("%Y%m%d"))
    [download_coin_data(coin, current_day) for coin in currencies_to_update.keys()]


def load_coin_from_file(coin):
    """load content from saved pickle file"""
    pickle_name = 'pickles\\' + str(coin)
    infile = open(pickle_name, 'rb')
    page_get = pickle.load(infile)
    infile.close()
    return page_get
############################


############################
# methods for Creating dataframes for each coin and placing all in one dictionary of {COIN : DATAFRAME}'s
def create_soup(coin):
    page = load_coin_from_file(coin)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def get_dates(soup):
    dates_raw = soup.find_all(class_= "cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")
    dates = [datetime.strptime(re.search('<div class="">(.+)</div>', d).group(1),'%b %d, %Y').date() for d in [str(dates_raw[i]) for i in range(len(dates_raw))]]
    return dates


def get_rates(soup):
    rates_raw = soup.find_all(class_="cmc-table__cell cmc-table__cell--right")
    rates = [re.search('<div class="">(.+)</div>', v).group(1).replace(',','') for v in [str(rates_raw[i]) for i in range(len(rates_raw))]]
    return rates


def create_dataframe(coin):
    soup = create_soup(coin)
    print(soup.prettify())
    dates = get_dates(soup)
    rates = get_rates(soup)
    col_names = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Cap']
    for i in range(len(col_names)-1):
        globals()[col_names[i+1]] = rates[i::6]
    df = pd.DataFrame(zip(dates, Open, High, Low, Close, Volume, Cap), columns=col_names)
    df[col_names[1:]] = round(df[col_names[1:]].astype(float),2)
    if df.empty:
        return None
    else:
        return df


def create_dictionary():
    curr = get_100_currencies()
    dictionary = {key: create_dataframe(key) for key in curr.keys()}
    pickle_name = 'dict.data'
    outfile = open(pickle_name, 'wb')
    pickle.dump(dictionary, outfile)
    outfile.close()
############################


def read_dictionary():
    """load content from saved pickle file"""
    pickle_name = 'dict.data'
    infile = open(pickle_name, 'rb')
    dictionary = pickle.load(infile)
    infile.close()
    return dictionary


if __name__ == '__main__':
    """use this command to update the pickle files we use"""
    # update_all_coins_data(get_100_currencies())
    # create_dictionary()
    """grey out the above functions after there first run"""
    dictionary = read_dictionary()
    print('items in dictionary:', len(dictionary))
    print('\n')

    print('items with data in dictionary:')
    for key, value in dictionary.items():
        if value is not None:
            print(key)

    print('\n')
    print('items without data in dictionary:', sum(value is None for value in dictionary.values()))
    for key, value in dictionary.items():
        if value is None:
            print(key)

