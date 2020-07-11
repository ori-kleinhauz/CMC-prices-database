import pymysql.cursors
import numpy as np
from ms1 import read_dictionary
import argparse
from tqdm import tqdm


# used to prevent AttributeError: 'numpy.float64' object has no attribute 'translate' when inserting values from
# dataframe to db
pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)


def create_connection(db, pswd):
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
        create_db(con, db)
        con = pymysql.connect(host='localhost',
                              user='root',
                              password=pswd,
                              charset='utf8mb4',
                              database=db,
                              cursorclass=pymysql.cursors.DictCursor)
        empty = True
    return con, empty


def create_db(con, name):
    """creates mysql database given its desired name"""
    with con.cursor() as cur:
        cur.execute(f"create database {name}")


def create_tables(con):
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


def insert_coins(con, dfs):
    """populates the coins table using the dataframes dictionary created in ms1.py"""
    with con.cursor() as cur:
        for n in tqdm(dfs.keys()):
            cur.execute("insert into coins (name) values (%s)", n)
        con.commit()


def insert_rates(con, dfs):
    """populates the rates table using the dataframes dictionary created in ms1.py"""
    with con.cursor() as cur:
        for i, df in enumerate(dfs.values()):
            for j in tqdm(range(len(df))):
                cur.execute("insert into rates (coin_id, date, open, high, low,  close, volume, cap)"
                            "values (%s, %s, %s, %s, %s, %s, %s, %s)",
                            (i + 1,
                             dfs[list(dfs.keys())[i]]['Date'][j],
                             dfs[list(dfs.keys())[i]]['Open'][j],
                             dfs[list(dfs.keys())[i]]['High'][j],
                             dfs[list(dfs.keys())[i]]['Low'][j],
                             dfs[list(dfs.keys())[i]]['Close'][j],
                             dfs[list(dfs.keys())[i]]['Volume'][j],
                             dfs[list(dfs.keys())[i]]['Cap'][j]
                             )
                            )
        con.commit()


def update_rates(con, dfs):
    """ searches for the latest date in the rates table and adds to it subsequent entries from the dataframes
    dictionary. gets the coin names from the dataframes dictionary, searches in the coins coins table, and writes
    their respective id's into the rates table, in case the top100 coins order was changed in the scraped website """
    with con.cursor() as cur:
        for (n, df) in dfs.items():
            cur.execute("select max(date) from rates join coins on rates.coin_id=coins.id where name=(%s)", n)
            result = cur.fetchall()
            max_date = result[0]
            cur.execute("select id from coins where name=(%s)", n)
            result = cur.fetchall()
            cid = result[0]
            df_new = df[df['Date'] > list(max_date.values())[0]]
            for j in tqdm(range(len(df_new))):
                cur.execute("insert into rates (coin_id, date, open, high, low,  close, volume, cap)"
                            "values (%s, %s, %s, %s, %s, %s, %s, %s)",
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


def main():
    """ uses the argparse module to read the user's mysql password and the database name from the command line. then,
    reads the dataframes dictionary created by ms1.py. updates the database if exists, otherwise creates and
    populates it """
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help='mysql password', type=str)
    parser.add_argument('db_name', help='database name', type=str)
    args = parser.parse_args()
    df_dict = read_dictionary()
    con, empty = create_connection(args.db_name, args.password)
    if not empty:
        update_rates(con, df_dict)
    else:
        create_tables(con)
        insert_coins(con, df_dict)
        insert_rates(con, df_dict)


if __name__ == '__main__':
    main()
