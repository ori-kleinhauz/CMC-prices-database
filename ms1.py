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
import logging


class Logger:
    def create_logger(self, name):
        """ creates a logger with a given name and adds a file handler to it"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(config.LOGGER_NAME)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(config.FORMAT)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        return logger

class Scraper:
    def get_100_currencies(self):
        """ creates and returns a dictionary of cryptocurrency names and their corresponding url suffixes to be used for
           scraping """
        homepage_get = requests.get(config.HOMEPAGE)
        sleep(config.SLEEP_INTERVAL)
        homepage_soup = BeautifulSoup(homepage_get.content, config.HTML_PARSER)
        top_100_currencies = {}
        links = [l for l in homepage_soup.findAll(config.A, href=True, title=True, class_= config.CMC_LINK)]
        for l in links:
            if config.CURRENCIES in l[config.HREF]:
                top_100_currencies[l[config.TITLE]] = l[config.HREF].split(config.SLASH)[config.TWO]
        return top_100_currencies

    def parse_100_currencies_links(self, coins):
        current_date = str(datetime.now().strftime(config.CURR_DATE_FORMAT))
        links = {coin: f'{config.CURRENCIES_PAGE}{coin}{config.CURRENCY_START}{current_date}'
                 for coin in coins.values()}
        return links

    def create_soup(self, url):
        """ creates and returns a beutifulsoup object of historical data for a given cryptocurrency"""
        coin_page_get = requests.get(url)
        coin_soup = BeautifulSoup(coin_page_get.content, config.HTML_PARSER)
        if not coin_page_get.ok:
            raise Exception(f"{config.REQ_FAIL}: {url}")
        return coin_soup


class Dataframe:
    def get_dates(self, soup):
        """ creates and returns a list of datetime objects for the history of a given cryptocurrency"""
        dates_raw = [d.text for d in
                     soup.findAll(config.TD, class_=config.CMC_LEFT)]
        dates = [datetime.strptime(d, config.DF_DATE_FORMAT).date() for d in dates_raw]
        return dates

    def get_rates(self, soup):
        """ creates and returns a list of rates(open, close etc.) for the history of a given cryptocurrency"""
        rates_raw = [d.text for d in soup.findAll(config.TD, class_=config.CMC_RIGHT)]
        rates = [r.replace(config.COMMA, config.EMPTY) for r in rates_raw]
        return rates

    def create_dataframe(self, value, url):
        """ creates a dataframe containing the rates of a cryptocurrency for each date in its history of existence"""
        soup = Scraper().create_soup(url)
        dates = self.get_dates(soup)
        rates = self.get_rates(soup)
        col_names = [config.DATE, config.OPEN, config.HIGH, config.LOW, config.CLOSE, config.VOLUME, config.CAP]
        opens = rates[config.ZERO::config.SIX]
        highs = rates[config.ONE::config.SIX]
        lows = rates[config.TWO::config.SIX]
        closes = rates[config.THREE::config.SIX]
        volumes = rates[config.FOUR::config.SIX]
        caps = rates[config.FIVE::config.SIX]
        df = pd.DataFrame(zip(dates, opens, highs, lows, closes, volumes, caps), columns=col_names)
        df[col_names[config.ONE:]] = round(df[col_names[config.ONE:]].astype(float), config.TWO)
        if df.empty:
            raise Exception(f'{config.EMPTY_DF}: {value}')
        else:
            return df


class Dictionary:
    def create_dataframes_dictionary(self, currencies, links):
        """ creates a dictionary of dataframes for each of the 100 cryptocurrencies scraped"""
        dfs_dict = {}
        for key, value in tqdm(currencies.items()):
            dfs_dict[key] = Dataframe().create_dataframe(value, links[value])
            sleep(config.SLEEP_INTERVAL)
        return dfs_dict

    def update_dataframes_dictionary(self, dictionary, currencies, links):
        """scans the current top 100 currencies list, and, in case any of them is/are not present in the dataframes
        dictionary, adds it/them """
        for key, value in tqdm(currencies.items()):
            if key not in dictionary.keys():
                dictionary[key] = Dataframe().create_dataframe(value, links[value])
                sleep(config.SLEEP_INTERVAL)

    def save_dictionary_to_pickle(self, dict):
        """ saves the dataframes dictionary to a pickle file"""
        pickle.dump(dict, open(config.DICTIONARY_FILENAME, config.WB))

    def read_dictionary_from_pickle(self):
        """ reads the dataframes dictionary from the pickle file"""
        with open(config.DICTIONARY_FILENAME, config.RB) as pfile:
            dfs_dict = pickle.load(pfile)
            return dfs_dict


def main():
    """ allows for dataframes dictionary creation, update, and printing. in addition, allows for creating and
    updating the mysql database using the dataframes dictionary """
    parser = argparse.ArgumentParser()
    parser.add_argument('-cdict', '--cdict', help='Create dictionary file', action='store_true')
    parser.add_argument('-udict', '--udict', help='Update dictionary file', action='store_true')
    parser.add_argument('-udb', nargs=2, metavar=('password', 'DB'), help='Update mysql DB')
    args = parser.parse_args()
    logger = Logger().create_logger(config.LOGGER_NAME)

    try:
        top_100_currencies = Scraper().get_100_currencies()
        links = Scraper().parse_100_currencies_links(top_100_currencies)
        dfs_dict = Dictionary().read_dictionary_from_pickle()
        db = ms2.MySQL_DB(dfs_dict)
        if args.udb:
            con, empty = db.create_connection(args.udb[1], args.udb[0])
            if not empty:
                logger.info(config.UPDATE_DB)
                db.update_db(con, dfs_dict)
            else:
                logger.info(config.CREATE_DB)
                db.create_tables(con)
                db.update_db(con, dfs_dict)
        if args.cdict:
            logger.info(config.CREATE_DICT)
            dfs_dict = Dictionary().create_dataframes_dictionary(top_100_currencies, links)
            Dictionary().save_dictionary_to_pickle(dfs_dict)
        if args.udict:
            logger.info(config.UPDATE_DICT)
            Dictionary().update_dataframes_dictionary(dfs_dict, top_100_currencies, links)
            Dictionary().save_dictionary_to_pickle(dfs_dict)

    except Exception as E:
        logger.error(repr(E))


if __name__ == '__main__':
    main()
