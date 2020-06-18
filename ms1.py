import requests
from bs4 import BeautifulSoup
import pickle
import datetime
from datetime import datetime
import pandas as pd
from pathlib import Path
import os
from time import sleep
HOMEPAGE = 'https://coinmarketcap.com/'


#############################
def get_100_currencies():
    page_get = requests.get(HOMEPAGE)
    soup = BeautifulSoup(page_get.content, 'html.parser')
    curr = {}
    links = [l for l in soup.findAll("a", href=True, title=True, class_='cmc-link')]
    for l in links:
        if 'currencies' in l['href']:
            curr[l['title']] = l['href'].split('/')[2]
    return curr


def download_coin_data(coin, end_date):
    """downloads the content online from CMC and saves to pickle file"""
    html = 'https://coinmarketcap.com/currencies/' + coin + '/historical-data/?start=20110428&end=' + end_date
    try:
        page_get = requests.get(html)
        Path("pickles\\").mkdir(parents=True, exist_ok=True)
        pickle_name = 'pickles\\' + str(coin)
        print(pickle_name.lower())
        outfile = open(pickle_name, 'wb')
        pickle.dump(page_get, outfile)
        outfile.close()
    except:
        print('error locating', coin, 'data. check possible name mismatch on CMC')


def update_all_coins_data(currencies_to_update):
    """updates the database of pickle file for the currencies provided"""
    current_day = str(datetime.now().strftime("%Y%m%d"))
    for coin, url in currencies_to_update.items():
        download_coin_data(url, current_day)
        sleep(20)


def load_coin_from_file(coin):
    """load content from saved pickle file"""
    pickle_name = 'pickles\\' + str(coin)
    infile = open(pickle_name.lower(), 'rb')
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
    dates_raw = [d.text for d in soup.findAll("td", class_= "cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")]
    dates = [datetime.strptime(d, '%b %d, %Y').date() for d in dates_raw]
    return dates


def get_rates(soup):
    rates_raw = [d.text for d in soup.findAll("td", class_= "cmc-table__cell cmc-table__cell--right")]
    rates = [r.replace(',','') for r in rates_raw]
    return rates


def create_dataframe(coin):
    soup = create_soup(coin)
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
    files_list = os.listdir('pickles')
    curr = {k: v for k, v in curr.items() if v.lower() in files_list}
    dictionary = {}
    for key, value in curr.items():
        try:
            dictionary[key] = create_dataframe(value.lower())
        except:
            pass
    pickle_name = 'dict.data'
    outfile = open(pickle_name, 'wb')
    pickle.dump(dictionary, outfile)
    outfile.close()
############################


############################
def read_dictionary():
    """load content from saved pickle file"""
    pickle_name = 'dict.data'
    infile = open(pickle_name, 'rb')
    dictionary = pickle.load(infile)
    infile.close()
    return dictionary
##############################


##############################
if __name__ == '__main__':
    """use these commands to update the pickle files we use and the dictionary file ---> dict.data"""
    # update_all_coins_data(get_100_currencies())
    # create_dictionary()
    """grey out the above functions after there first run"""
    dictionary = read_dictionary()
    for key in dictionary.keys():
        print(key)
    print('\n' + 'items in dictionary:', len(dictionary))
    print(dictionary['Algorand'])
