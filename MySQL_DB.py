import numpy as np
import pymysql.cursors
from tqdm import tqdm
import config

# used to prevent AttributeError: 'numpy.float64' object has no attribute 'translate' when inserting values from
# dataframe to db
pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)


class MySQL_DB:
    def __init__(self, dfs_dict, logger):
        self.dfs_dict = dfs_dict
        self.logger = logger

    def create_connection(self, db, pswd):
        """ attempts to connect to an existing mysql database given the its name and the user's password.
        in case it doesn't exist, creates it and connects to it. returns the connection object and the db's status
        (assumes the db isn't empty if exists)"""
        self.logger.info(config.CON_DB)
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
        self.logger.info(config.CON_SUC)
        return con, empty

    def create_db(self, con, name):
        self.logger.info(config.CREATING_DB)
        """creates mysql database given its desired name"""
        with con.cursor() as cur:
            cur.execute(f'{config.CREATE_DB} {name}')

    def create_tables(self, con):
        """creates the coins and rates tables in the connected database.
         uses unique primary keys for each coin and each rate entry,
         and a foreign one-to-many key from the coins table to the rates table"""
        self.logger.info(config.CREATE_TABLES)
        with con.cursor() as cur:
            cur.execute(config.CREATE_COINS)
            cur.execute(config.CREATE_RATES)
        self.logger.info(config.COMPLETE)

    def insert_coins(self, con):
        """populates the coins table using the dataframes dictionary created in ms1.py.
        if a certain coin replaced another, adds it to the end of the table using auto-increment"""
        self.logger.info(config.UP_COINS)
        with con.cursor() as cur:
            cur.execute(config.SELECT_NAME)
            result = cur.fetchall()
            coin_names = [coin[config.NAME] for coin in result]
            for n, df in tqdm(self.dfs_dict.items()):
                if n not in coin_names:
                    cur.execute(config.INSERT_COINS, n)
            con.commit()
        self.logger.info(config.COMPLETE)

    def insert_rates(self, con):
        """ searches for missing dates per coin in the rates table and adds to it those entries from the respective
        dataframe in the dataframes dictionary. gets the coin names from the dataframes dictionary and writes their
        respective id's from the coins table into the rates table. if the rates table is empty (as is the case for a
        new db), or a new coin was added to the coins table, it will add the entire dataframe(s) """
        self.logger.info(config.UP_RATES)
        with con.cursor() as cur:
            for n, df in self.dfs_dict.items():
                cur.execute(config.SELECT_ID, n)
                result = cur.fetchall()
                coin_id = result[config.ZERO][config.ID]
                cur.execute(config.SELECT_DATES, coin_id)
                result = cur.fetchall()
                df = df[~df[config.DATE].isin([r[config.DATE_LOWER] for r in result])]
                if not df.empty:
                    for j in tqdm(df.index):
                        cur.execute(config.INSERT_RATES,
                                    (coin_id,
                                     df[config.DATE][j],
                                     df[config.OPEN][j],
                                     df[config.HIGH][j],
                                     df[config.LOW][j],
                                     df[config.CLOSE][j],
                                     df[config.VOLUME][j],
                                     df[config.CAP][j]
                                     )
                                    )
            con.commit()
        self.logger.info(config.COMPLETE)


    def update_db(self, con):
        self.logger.info(config.UPDATE_DB)
        self.insert_coins(con)
        self.insert_rates(con)
