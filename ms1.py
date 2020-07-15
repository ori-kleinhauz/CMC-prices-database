"""
Top 100 crypto currencies database scraper

Authors:
Ori Kleinhauz
Yuval Herman

"""
import grequests
import requests
from bs4 import BeautifulSoup
import pickle
import datetime
from datetime import datetime
import pandas as pd
from pathlib import Path
import os
import shutil
from tqdm import tqdm
import sys
import argparse
import config


#############################
def get_100_currencies():
    """ creates and returns a dictionary of cryptocurrency names and their corresponding url suffixes to be used for
       scraping """
    page_get = requests.get(config.HOMEPAGE)
    soup = BeautifulSoup(page_get.content, 'html.parser')
    curr = {}
    links = [l for l in soup.findAll("a", href=True, title=True, class_='cmc-link')]
    for l in tqdm(links):
        if 'currencies' in l['href']:
            curr[l['title']] = l['href'].split('/')[2]
    return curr


def update_all_coins_data(currencies_to_update):
    """updates the database of pickle file for the currencies provided"""
    current_day = str(datetime.now().strftime("%Y%m%d"))
    coin_list = list(currencies_to_update.keys())
    links_list = [f'{config.CURRENCIES_PAGE}{value}{config.CURRENCY_START}{current_day}' for value in
                  currencies_to_update.values()]
    page_responses = [grequests.get(link) for link in links_list]
    Path(f'{config.PICKLE_FOLDER}\\').mkdir(parents=True, exist_ok=True)
    for x, soup in enumerate(grequests.map(page_responses)):
        try:
            pickle_name = f'{config.PICKLE_FOLDER}\\{str(coin_list[x])}'
            print(pickle_name.lower())
            outfile = open(pickle_name, 'wb')
            pickle.dump(soup, outfile)
            outfile.close()
        except ConnectionError:
            print(f'{config.ERRORS_MESSAGES["Connection_failed"]}')


def load_coin_from_file(coin):
    """load content from saved pickle file"""
    pickle_name = f'{config.PICKLE_FOLDER}\\{str(coin)}'
    infile = open(pickle_name.lower(), 'rb')
    page_get = pickle.load(infile)
    infile.close()
    return page_get


############################


############################
# methods for Creating dataframes for each coin and placing all in one dictionary of {COIN : DATAFRAME}'s
def create_soup(coin):
    """ creates and returns a beutifulsoup object of historical data for a given cryptocurrency"""
    page = load_coin_from_file(coin)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def get_dates(soup):
    """ creates and returns a list of datetime objects for the history of a given cryptocurrency"""
    dates_raw = [d.text for d in
                 soup.findAll("td", class_="cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")]
    dates = [datetime.strptime(d, '%b %d, %Y').date() for d in dates_raw]
    return dates


def get_rates(soup):
    """ creates and returns a list of rates(open, close etc.) for the history of a given cryptocurrency"""
    rates_raw = [d.text for d in soup.findAll("td", class_="cmc-table__cell cmc-table__cell--right")]
    rates = [r.replace(',', '') for r in rates_raw]
    return rates


def create_dataframe(coin):
    """ creates a dataframe containing the rates of a cryptocurrency for each date in its history of existence"""
    try:
        soup = create_soup(coin)
        if soup.is_empty_element:
            raise RuntimeError(f'{config.ERRORS_MESSAGES["read_soup"]}')

        dates = get_dates(soup)
        if len(dates) == 0:
            raise RuntimeError(f'{config.ERRORS_MESSAGES["read_dates"]}')

        rates = get_rates(soup)
        if len(rates) == 0:
            raise RuntimeError(f'{config.ERRORS_MESSAGES["read_rates"]}')

        col_names = config.COL_NAMES
        opens = rates[0::6]
        highs = rates[1::6]
        lows = rates[2::6]
        closes = rates[3::6]
        volumes = rates[4::6]
        caps = rates[5::6]

        df = pd.DataFrame(zip(dates, opens, highs, lows, closes, volumes, caps), columns=col_names)
        df[col_names[1:]] = round(df[col_names[1:]].astype(float), 2)

        if df.empty:
            return None
        else:
            return df
    except:
        raise


def create_dictionary(curr):
    """ creates a dictionary of dataframes for each of the 100 cryptocurrencies scraped"""
    files_list = os.listdir(config.PICKLE_FOLDER)
    curs = {k: v for k, v in curr.items() if v.lower() in files_list}
    dictionary = {}
    print('Creating Dictionary...')
    for key, value in tqdm(curs.items()):
        try:
            dictionary[key] = create_dataframe(value.lower())
        except Exception as E:
            raise E
    pickle_name = f'\\{config.DICTIONARY_NAME}'
    outfile = open(pickle_name, 'wb')
    pickle.dump(dictionary, outfile)
    outfile.close()
    try:
        shutil.rmtree(config.PICKLE_FOLDER, ignore_errors=True)
    except:
        raise NotADirectoryError(f'{config.ERRORS_MESSAGES["delete_pickles"]}')


############################


############################
def read_dictionary():
    """load content from saved pickle file"""
    try:
        pickle_name = config.DICTIONARY_NAME
        infile = open(pickle_name, 'rb')
        dictionary = pickle.load(infile)
        infile.close()
        return dictionary
    except:
        raise FileNotFoundError(config.ERRORS_MESSAGES['read_dictionary'])


##############################
def choose_coin():
    """prompts the user to pick a currency from the dictionary and displays its data"""
    dictionary = read_dictionary()
    for counter, key in enumerate(dictionary.keys()):
        print(counter + 1, ':', key)
    print('---above is a list of keys for which historical information is available in the dictionary\n')
    while True:
        coin_to_display = input('\nPlease choose a coin from the above list to display its history (or press q to '
                                'exit): ')
        if coin_to_display == 'q':
            sys.exit(0)
        if coin_to_display in dictionary.keys():
            print(coin_to_display, '\n', dictionary[coin_to_display])
        else:
            print(coin_to_display, ' - is not a coin in the available database')


##############################
def main():
    """ updates the dictionary containing historical data for each cryptocurrency(optional) and prompts the user to
            choose one of them, then displays its data """
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-u', '--u', help='Update database', action='store_true')
        parser.add_argument('-c', '--c', help='Choose coin', action='store_true')
        args = parser.parse_args()
        if args.u:
            curr = get_100_currencies()
            update_all_coins_data(curr)
            create_dictionary(curr)
        if args.c:
            choose_coin()
    except Exception as E:
        print(E)

##############################


if __name__ == '__main__':
    main()
