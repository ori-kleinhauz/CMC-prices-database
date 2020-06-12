import requests
from bs4 import BeautifulSoup
import pickle
import datetime
from datetime import datetime
import pandas as pd
MOST_TRADED_CRYPTOS = 'https://trading-education.com/top-100-cryptocurrencies-on-coinmarketcap-in-one-sentence'


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


def experiments(page, coin):
    """this is a general function where we can try out anything.."""
    soup = BeautifulSoup(page.content, 'html.parser')
    # print(soup.prettify())
    # (soup.prettify())

    date_dirty = soup.find_all(class_= "cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")
    test_dirty = [str(date_dirty[i]) for i in range(len(date_dirty))]
    # print(soup.prettify())
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
    col_names = ['date','open','high','low','close','volume','market cap']
    df = pd.DataFrame(zip(datetime_obj,opens,highs,lows ,closes,volumes,caps), columns=col_names)
    df[col_names[1:]] = round(df[col_names[1:]].astype(float),2)
    # print(df)
    return df

def create_dictionary():
    curr = get_100_currencies()
    dictionary = dict((key, experiments(load_coin_from_file(key), key)) for key in curr.keys())
    for key, value in sorted(dictionary.items()):
        print(key, value)


    # pickle_name = 'dict.data'
    # outfile = open(pickle_name, 'wb')
    # pickle.dump(dictionary, outfile)
    # outfile.close()


if __name__ == '__main__':
    """use this command to update the pickle files we use"""
    # update_all_coins_data(get_100_currencies())
    # create_dictionary()
    # experiments(load_coin_from_file('IOTA'), 'IOTA')



