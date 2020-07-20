import pymysql.cursors
import numpy as np
from tqdm import tqdm

# used to prevent AttributeError: 'numpy.float64' object has no attribute 'translate' when inserting values from
# dataframe to db
pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)


class MySQL_DB:
    def __init__(self, dfs_dict):
        self.dfs_dict = dfs_dict

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

    def create_tables(self, con):
        """creates the coins and rates tables in the connected database.
         uses unique primary keys for each coin and each rate entry,
         and a foreign one-to-many key from the coins table to the rates table"""
        with con.cursor() as cur:
            cur.execute("create table coins (id int primary key auto_increment, name char(255))")
            cur.execute("""create table rates
                            (id int primary key auto_increment, 
                            coin_id int, 
                            date date, 
                            open float, 
                            high float, 
                            low float,
                            close float, 
                            volume float, 
                            cap float,
                            foreign key (coin_id) references coins(id))""")

    def insert_coins(self, con, dfs):
        """populates the coins table using the dataframes dictionary created in ms1.py"""
        with con.cursor() as cur:
            for n in tqdm(dfs.keys()):
                cur.execute("insert into coins (name) values (%s)", n)
            con.commit()

    def insert_rates(self, con, dfs):
        """populates the rates table using the dataframes dictionary created in ms1.py"""
        with con.cursor() as cur:
            for n, df in dfs.items():
                cur.execute("select id from coins where name=(%s)", n)
                result = cur.fetchall()
                coin_id = result[0]['id']
                self.insert_rates_from_df(cur, df, coin_id)
            con.commit()

    def update_rates(self, con, dfs):
        """ searches for missing dates per coin in the rates table and adds to it those entries from the respective
        dataframe in the dataframes dictionary. gets the coin names from the dataframes dictionary and writes their
        respective id's from the coins table into the rates table. """
        with con.cursor() as cur:
            for n, df in dfs.items():
                cur.execute("select id from coins where name=(%s)", n)
                result = cur.fetchall()
                coin_id = result[0]['id']
                cur.execute("select date from rates")
                result = cur.fetchall()
                df = df[~df['Date'].isin([r['date'] for r in result])]
                self.insert_rates_from_df(cur, df, coin_id)
            con.commit()

    def insert_rates_from_df(self, cur, df, coin_id):
        for j in tqdm(df.index):
            cur.execute("insert into rates (coin_id, date, open, high, low,  close, volume, cap)"
                        "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (coin_id,
                         df['Date'][j],
                         df['Open'][j],
                         df['High'][j],
                         df['Low'][j],
                         df['Close'][j],
                         df['Volume'][j],
                         df['Cap'][j]
                         )
                        )


