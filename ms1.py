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
from MySQL_DB import MySQL_DB
import logging
import api


def create_logger(name):
    """ creates a logger with a given name and adds a file handler to it"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(config.LOGGER_NAME)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(config.FORMAT)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def get_100_currencies():
    """ creates and returns a dictionary of cryptocurrency names and their corresponding urls to be used for
       scraping """
    current_date = str(datetime.now().strftime(config.CURR_DATE_FORMAT))
    homepage_get = requests.get(config.HOMEPAGE)
    sleep(config.SLEEP_INTERVAL)
    homepage_soup = BeautifulSoup(homepage_get.content, config.HTML_PARSER)
    top_100_currencies = {}
    links = [l for l in homepage_soup.findAll(config.A, href=True, title=True, class_=config.CMC_LINK)]
    for l in links:
        if config.CURRENCIES in l[config.HREF]:
            coin = l[config.HREF].split(config.SLASH)[config.TWO]
            top_100_currencies[l[config.TITLE]] = f'{config.CURRENCIES_PAGE}{coin}{config.CURRENCY_START}{current_date}'
    return top_100_currencies


def create_soup(url):
    """ creates and returns a beutifulsoup object of historical data for a given cryptocurrency"""
    coin_page_get = requests.get(url)
    coin_soup = BeautifulSoup(coin_page_get.content, config.HTML_PARSER)
    if not coin_page_get.ok:
        raise Exception(f"{config.REQ_FAIL}: {url}")
    return coin_soup


def get_dates(soup):
    """ creates and returns a list of datetime objects for the history of a given cryptocurrency"""
    dates_raw = [d.text for d in
                 soup.findAll(config.TD, class_=config.CMC_LEFT)]
    dates = [datetime.strptime(d, config.DF_DATE_FORMAT).date() for d in dates_raw]
    return dates


def get_rates(soup):
    """ creates and returns a list of rates(open, close etc.) for the history of a given cryptocurrency"""
    rates_raw = [d.text for d in soup.findAll(config.TD, class_=config.CMC_RIGHT)]
    rates = [r.replace(config.COMMA, config.EMPTY) for r in rates_raw]
    return rates


def create_dataframe(key, url):
    """ creates a dataframe containing the rates of a cryptocurrency for each date in its history of existence"""
    soup = create_soup(url)
    if soup.is_empty_element:
        raise Exception(f'{config.SOUP_ERROR} {key}')
    dates = get_dates(soup)
    if len(dates) == 0:
        raise Exception(f'{config.DATE_ERROR} {key}')
    rates = get_rates(soup)
    if len(rates) == 0:
        raise Exception(f'{config.RATE_ERROR} {key}')
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
        raise Exception(f'{config.EMPTY_DF}: {key}')
    else:
        return df


def create_dataframes_dictionary(currencies):
    """ creates a dictionary of dataframes for each of the 100 cryptocurrencies scraped"""
    dfs_dict = {}
    for key, value in tqdm(currencies.items()):
        dfs_dict[key] = create_dataframe(key, value)
        sleep(config.SLEEP_INTERVAL)
    return dfs_dict


def update_dataframes_dictionary(dictionary, currencies):
    """scans the current top 100 currencies list, and, in case any of them is/are not present in the dataframes
    dictionary, adds it/them """
    for key, value in tqdm(currencies.items()):
        if key not in dictionary.keys():
            dictionary[key] = create_dataframe(key, value)
            sleep(config.SLEEP_INTERVAL)


def save_dictionary_to_pickle(dict):
    """ saves the dataframes dictionary to a pickle file"""
    pickle.dump(dict, open(config.DICTIONARY_FILENAME, config.WB))


def read_dictionary_from_pickle():
    """ reads the dataframes dictionary from the pickle file"""
    with open(config.DICTIONARY_FILENAME, config.RB) as pfile:
        dfs_dict = pickle.load(pfile)
        return dfs_dict


def create_and_save_dict(logger, top_100_currencies):
    """ creates, logs, and saves dataframes dictionary to file"""
    logger.info(config.CREATE_DICT)
    dfs_dict = create_dataframes_dictionary(top_100_currencies)
    logger.info(config.SAVE_DICT)
    save_dictionary_to_pickle(dfs_dict)


def update_and_save_dict(logger, dfs_dict, top_100_currencies):
    """ updates, logs, and saves dataframes dictionary to file"""
    logger.info(config.UPDATE_DICT)
    update_dataframes_dictionary(dfs_dict, top_100_currencies)
    logger.info(config.SAVE_DICT)
    save_dictionary_to_pickle(dfs_dict)


def save_api_to_pickle(api_data):
    """ saves the api dataframe to a pickle file"""
    pickle.dump(api_data, open(config.API_FILENAME, config.WB))


def read_api_from_pickle():
    """ saves the api dataframe to a pickle file"""
    with open(config.API_FILENAME, config.RB) as pfile:
        api_data = pickle.load(pfile)
        return api_data


def create_and_save_api(logger):
    logger.info(config.FETCH_API)
    api_data = api.get_api_data()
    logger.info(config.SAVE_API)
    save_api_to_pickle(api_data)


def main():
    """ allows for dataframes dictionary creation, update, and printing. in addition, allows for creating and
    updating the mysql database using the dataframes dictionary """
    parser = argparse.ArgumentParser()
    parser.add_argument(config.CDICT, f'{config.SPACE}{config.CDICT}', help=config.CDICT_HELP, action=config.ST)
    parser.add_argument(config.CAPI, f'{config.SPACE}{config.CAPI}', help=config.UAPI_HELP, action=config.ST)
    parser.add_argument(config.UDICT, f'{config.SPACE}{config.UDICT}', help=config.UDICT_HELP, action=config.ST)
    parser.add_argument(config.UDB, nargs=config.TWO, metavar=(config.PASSWORD, config.DB), help=config.UDB_HELP)
    args = parser.parse_args()
    logger = create_logger(config.LOGGER_NAME)
    top_100_currencies = get_100_currencies()

    try:
        logger.info(config.READ_DICT)
        dfs_dict = read_dictionary_from_pickle()
        logger.info(config.SUCCESS)
    except FileNotFoundError:
        logger.error(config.NO_DICT)
        create_and_save_dict(logger, top_100_currencies)
        logger.info(config.READ_DICT)
        dfs_dict = read_dictionary_from_pickle()
        logger.info(config.SUCCESS)
    try:
        logger.info(config.READ_API)
        api_data = read_api_from_pickle()
        logger.info(config.SUCCESS)
    except FileNotFoundError:
        logger.error(config.NO_API)
        create_and_save_api(logger)
        logger.info(config.READ_API)
        api_data = read_api_from_pickle()
        logger.info(config.SUCCESS)

    try:
        if args.udb:
            db = MySQL_DB(dfs_dict, api_data, logger)
            con, empty = db.create_connection(args.udb[config.ONE], args.udb[config.ZERO])
            if not empty:
                db.update_db(con)
            else:
                db.create_tables(con)
                db.update_db(con)
        if args.cdict:
            create_and_save_dict(logger, top_100_currencies)
        if args.capi:
            create_and_save_api(logger)
        if args.udict:
            update_and_save_dict(logger, dfs_dict, top_100_currencies)


    except Exception as E:
        logger.error(E, exc_info=True)


if __name__ == '__main__':
    main()
