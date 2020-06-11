import requests
from bs4 import BeautifulSoup
import pickle
import datetime
import re
from datetime import datetime
import pandas as pd


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
    page = load_coin_pickle_to_object('ethereum')
    print(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup.prettify())
    # (soup.prettify())
    date_dirty = soup.find_all(class_= "cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")
    test_dirty = [str(date_dirty[i]) for i in range(len(date_dirty))]
    end = test_dirty[0].index('</div></td>')
    test_clean = [t[end - 12:end] for t in test_dirty]
    datetime_obj = []
    alsotest = datetime.strptime(test_clean[0], '%b %d, %Y').date()
    datetime_obj = [datetime.strptime(t, '%b %d, %Y').date() for t in test_clean]
    val_dirty = soup.find_all(class_="cmc-table__cell cmc-table__cell--right")
    val_str = [str(val_dirty[i]) for i in range(len(val_dirty))]
    # values_dirty = soup.find_all(class = "cmc-table__cell cmc-table__cell--right")
    vals_split = [v.split('>') for v in val_str]
    vals_numbers = [v[-3] for v in vals_split]
    vals_clean = [v[:-5].replace(',','') for v in vals_numbers]
    opens = vals_clean[0::6]
    highs = vals_clean[1::6]
    lows = vals_clean[2::6]
    closes = vals_clean[3::6]
    volumes = vals_clean[4::6]
    caps = vals_clean[5::6]
    print(opens)
    print(highs)
    print(lows)
    print(closes)
    print(volumes)
    print(caps)
    col_names = ['date','open','high','low','close','volume','market cap']
    df = pd.DataFrame(zip(datetime_obj,opens,highs,lows ,closes,volumes,caps), columns=col_names)
    df[col_names[1:]]  = round(df[col_names[1:]].astype(float),2)
    print(df)
if __name__ == '__main__':
    """use this command to update the pickle files we use"""
    # update_coins_data(['bitcoin', 'ethereum'])
    experiments()

