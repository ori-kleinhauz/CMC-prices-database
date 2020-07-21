"""
Top 100 crypto currencies database scraper

Authors:
Ori Kleinhauz
Yuval Herman

"""

import requests
from bs4 import BeautifulSoup
import pickle
import datetime
from datetime import datetime
import pandas as pd
from time import sleep
from tqdm import tqdm
import argparse
import config
import ms2


class Scraper:
    def get_100_currencies(self):
        """ creates and returns a dictionary of cryptocurrency names and their corresponding url suffixes to be used for
           scraping """
        homepage_get = requests.get(config.HOMEPAGE)
        sleep(5)
        homepage_soup = BeautifulSoup(homepage_get.content, 'html.parser')
        top_100_currencies = {}
        links = [l for l in homepage_soup.findAll("a", href=True, title=True, class_='cmc-link')]
        for l in links:
            if 'currencies' in l['href']:
                top_100_currencies[l['title']] = l['href'].split('/')[2]
        return top_100_currencies

    def parse_100_currencies_links(self, coins):
        current_date = str(datetime.now().strftime("%Y%m%d"))
        links = {coin: f'{config.CURRENCIES_PAGE}{coin}{config.CURRENCY_START}{current_date}' for coin in
                 coins.values()}
        return links

    def create_soup(self, url):
        """ creates and returns a beutifulsoup object of historical data for a given cryptocurrency"""
        coin_page_get = requests.get(url)
        coin_soup = BeautifulSoup(coin_page_get.content, 'html.parser')
        if not coin_page_get.ok:
            raise Exception(f"request failed: {url}")
        return coin_soup


class Dataframe:

    def get_dates(self, soup):
        """ creates and returns a list of datetime objects for the history of a given cryptocurrency"""
        dates_raw = [d.text for d in
                     soup.findAll("td", class_="cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left")]
        dates = [datetime.strptime(d, '%b %d, %Y').date() for d in dates_raw]
        return dates

    def get_rates(self, soup):
        """ creates and returns a list of rates(open, close etc.) for the history of a given cryptocurrency"""
        rates_raw = [d.text for d in soup.findAll("td", class_="cmc-table__cell cmc-table__cell--right")]
        rates = [r.replace(',', '') for r in rates_raw]
        return rates

    def create_dataframe(self, value, url):
        """ creates a dataframe containing the rates of a cryptocurrency for each date in its history of existence"""
        soup = Scraper().create_soup(url)
        dates = self.get_dates(soup)
        rates = self.get_rates(soup)
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
            raise Exception(f"empty df created: {value}")
        else:
            return df


class Dictionary:
    def create_dataframes_dictionary(self, currencies, links):
        """ creates a dictionary of dataframes for each of the 100 cryptocurrencies scraped"""
        dfs_dict = {}
        for key, value in tqdm(currencies.items()):
            dfs_dict[key] = Dataframe().create_dataframe(value, links[value])
            sleep(5)
        return dfs_dict

    def save_dictionary_to_pickle(self, dict):
        """ saves the dataframes dictionary to a pickle file"""
        pickle.dump(dict, open("dfs_dict.p", "wb"))

    def read_dictionary_from_pickle():
        """ reads the dataframes dictionary from the pickle file"""
        with open('dfs_dict.p', 'rb') as pfile:
            dfs_dict = pickle.load(pfile)
            return dfs_dict


def main():
    """ updates the dictionary containing historical data for each cryptocurrency(optional) and prompts the user to
            choose one of them, then displays its data """
    parser = argparse.ArgumentParser()
    parser.add_argument('-udict', '--udict', help='Update dictionary file', action='store_true')
    parser.add_argument('-c', '--c', help='Choose coin from dictionary', action='store_true')
    parser.add_argument('-udb', nargs=2, metavar=('password', 'DB'), help='Update mysql DB')
    args = parser.parse_args()

    try:
        dfs_dict = Dictionary.read_dictionary_from_pickle()
        db = ms2.MySQL_DB(dfs_dict)
        con, empty = ms2.MySQL_DB(dfs_dict).create_connection(args.udb[1], args.udb[0])
        if args.udb:
            if not empty:
                db.update_db(con, dfs_dict)
            else:
                db.create_tables(con)
                db.update_db(con, dfs_dict)
        if args.udict:
            top_100_currencies = Scraper().get_100_currencies()
            links = Scraper().parse_100_currencies_links(top_100_currencies)
            dfs_dict = Dictionary().create_dataframes_dictionary(top_100_currencies, links)
            Dictionary().save_dictionary_to_pickle(dfs_dict)

    except Exception as E:
        print(E)


if __name__ == '__main__':
    main()
