import pandas as pd
import os
import config
from tqdm import tqdm
import pymysql.cursors
import numpy as np

# used to prevent AttributeError: 'numpy.float64' object has no attribute 'translate' when inserting values from
# dataframe to db
pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)


class DB:
    def __init__(self, dictionary):
        self.dictionary = dictionary

    def get_coin_date_value(self, coin, date):
        if coin not in self.dictionary.keys():
            return 'coin supplied not in database'
        else:
            try:
                df = self.dictionary.get(coin)
                return df.loc[df['Date'] == pd.to_datetime(date), 'Close'].values[0].astype(float)
            except:
                ValueError('Date was not supplied as expected. please use either DD-MM-YYYY/ YYYYMMDD / DD/MM/YYYY')

    def get_all_coin_data(self, coin):
        if coin not in self.dictionary.keys():
            return 'coin supplied not in database'
        else:
            return self.dictionary.get(coin)

    def get_last_date_per_coin(self, coin):
        if coin not in self.dictionary.keys():
            return 'coin supplied not in database'
        else:
            df = self.dictionary.get(coin)
            return df['Date'].max()

    def get_prices_between_dates(self, coin, begin, end):
        if coin not in self.dictionary.keys():
            return 'coin supplied not in database'
        else:
            try:
                df = self.dictionary.get(coin)
                cond = (df['Date'] >= pd.to_datetime(begin)) & (df['Date'] <= pd.to_datetime(end))
                print(cond)
                return df[cond]
            except:
                ValueError('Dates were not supplied as expected. please use either DD-MM-YYYY/ YYYYMMDD / DD/MM/YYYY'
                           '\nexample for valid parameters input: "Bitcoin 01/01/2019 31/12/2019"')

    def get_coin_len_records(self, coin):
        if coin not in self.dictionary.keys():
            return 'coin supplied not in database'
        else:
            return len(self.dictionary.get(coin))

    def update_rates(self, con):
        """ searches for the latest date in the rates table and adds to it subsequent entries from the dataframes
        dictionary. gets the coin names from the dataframes dictionary, searches in the coins coins table, and writes
        their respective id's into the rates table, in case the top100 coins order was changed in the scraped website """
        with con.cursor() as cur:
            for (n, df) in self.dictionary.items():
                cur.execute(config.GET_MAX_DATE_IN_DB, n)
                result = cur.fetchall()
                max_date = result[0]
                cur.execute(config.GET_COIN_ID_IN_DB, n)
                result = cur.fetchall()
                cid = result[0]
                df_new = df[df['Date'] > list(max_date.values())[0]]
                for j in tqdm(range(len(df_new))):
                    cur.execute(config.INSERT_NEW_RATE,
                                (list(cid.values())[0],
                                 df_new['Date'][j],
                                 df_new['Open'][j],
                                 df_new['High'][j],
                                 df_new['Low'][j],
                                 df_new['Close'][j],
                                 df_new['Volume'][j],
                                 df_new['Cap'][j]
                                 )
                                )
            con.commit()

    def insert_rates(self, con):
        """populates the rates table using the dataframes dictionary created in ms1.py"""
        with con.cursor() as cur:
            for i, df in enumerate(self.dictionary.values()):
                for j in tqdm(range(len(df))):
                    cur.execute(config.INSERT_NEW_RATE,
                                (i + 1,
                                 self.dictionary[list(self.dictionary.keys())[i]]['Date'][j],
                                 self.dictionary[list(self.dictionary.keys())[i]]['Open'][j],
                                 self.dictionary[list(self.dictionary.keys())[i]]['High'][j],
                                 self.dictionary[list(self.dictionary.keys())[i]]['Low'][j],
                                 self.dictionary[list(self.dictionary.keys())[i]]['Close'][j],
                                 self.dictionary[list(self.dictionary.keys())[i]]['Volume'][j],
                                 self.dictionary[list(self.dictionary.keys())[i]]['Cap'][j]
                                 )
                                )
            con.commit()

    def insert_coins(self, con):
        """populates the coins table using the dataframes dictionary created in ms1.py"""
        with con.cursor() as cur:
            for n in tqdm(self.dictionary.keys()):
                cur.execute(config.INSERT_NEW_COIN, n)
            con.commit()

    def create_tables(self, con):
        """creates the coins and rates tables in the connected database.
         uses unique primary keys for each coin and each rate entry,
         and a foreign one-to-many key from the coins table to the rates table"""
        with con.cursor() as cur:
            cur.execute(config.CREATE_TABLE_DATES)
            cur.execute(config.CREATE_TABLE_RATES)

    def create_connection(self, db, pswd):
        """ attempts to connect to an existing mysql database given the its name and the user's password.
        in case it doesn't exist, creates it and connects to it. returns the connection object and the db's status
        (assumes the db isn't empty if exists)"""
        try:
            con = pymysql.connect(host='localhost',
                                  user='root',
                                  password=pswd,
                                  charset='utf8mb4',
                                  database=db,
                                  cursorclass=pymysql.cursors.DictCursor)
            empty = False
        except pymysql.err.InternalError:
            con = pymysql.connect(host='localhost',
                                  user='root',
                                  password=pswd,
                                  charset='utf8mb4',
                                  cursorclass=pymysql.cursors.DictCursor)
            self.create_db(con, db)
            con = pymysql.connect(host='localhost',
                                  user='root',
                                  password=pswd,
                                  charset='utf8mb4',
                                  database=db,
                                  cursorclass=pymysql.cursors.DictCursor)
            empty = True
        return con, empty

    def create_db(self, con, name):
        """creates mysql database given its desired name"""
        with con.cursor() as cur:
            cur.execute(f"create database {name}")

# if __name__ == '__main__':
#     dict1 = DB(read_dictionary())
#     print(dict1.get_coin_date_value('Bitcoin', '10-10-2017'))
#     print(dict1.get_all_coin_data('Bitcoin'))
#     print(dict1.get_last_date_per_coin('Bitcoin'))
#     print(dict1.get_prices_between_dates('Bitcoin', '01012019', '31/12/2019'))
#     print(dict1.get_coin_len_records('Bitcoin'))
