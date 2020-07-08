import pymysql.cursors
import numpy as np
from ms1 import read_dictionary
import argparse

pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)


def create_connection(db, pswd):

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
    return con


def create_db(con, name):
    with con.cursor() as cur:
        cur.execute(f"create database {name}")


def create_tables(con):
    with con.cursor() as cur:
        cur.execute("create table coins (id int primary key, currency char(255))")
        cur.execute("""create table rates
                        (id int primary key auto_increment, 
                        coin_id int, 
                        date date, 
                        open float, 
                        high float, 
                        close float, 
                        volume float, 
                        cap float,
                        foreign key (coin_id) references coins(id))""")


def insert_values(con, dfs):
    with con.cursor() as cur:
        for i in range(len(dfs.keys())):
            cur.execute("insert into coins (id, currency) values (%s, %s)", (i, list(dfs.keys())[i]))
        con.commit()

        for i in range(len(dfs.keys())):
            for j in range(len(dfs[list(dfs.keys())[i]])):
                cur.execute("insert into rates (coin_id, date, open, high, close, volume, cap)"
                            "values (%s, %s, %s, %s, %s, %s, %s)",
                            (i,
                             dfs[list(dfs.keys())[i]]['Date'][j],
                             dfs[list(dfs.keys())[i]]['Open'][j],
                             dfs[list(dfs.keys())[i]]['High'][j],
                             dfs[list(dfs.keys())[i]]['Close'][j],
                             dfs[list(dfs.keys())[i]]['Volume'][j],
                             dfs[list(dfs.keys())[i]]['Cap'][j]
                             )
                            )
        con.commit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help='mysql password', type=str)
    parser.add_argument('db_name', help='database name', type=str)
    args = parser.parse_args()
    df_dict = read_dictionary()
    con = create_connection(args.db_name, args.password)
    create_tables(con)
    insert_values(con, df_dict)


if __name__ == '__main__':
    main()
