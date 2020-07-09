import pymysql.cursors
import numpy as np
from ms1 import read_dictionary
import argparse

pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)


def create_connection(db, pswd):
    try:
        con = pymysql.connect(host='localhost',
                              user='root',
                              password=pswd,
                              charset='utf8mb4',
                              database=db,
                              cursorclass=pymysql.cursors.DictCursor)
        exists = True
    except:
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
        exists = False
    return con, exists


def create_db(con, name):
    with con.cursor() as cur:
        cur.execute(f"create database {name}")


def create_tables(con):
    with con.cursor() as cur:
        cur.execute("create table coins (id int primary key, name char(255))")
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
    with con.cursor() as cur:
        for i, n in enumerate(dfs.keys()):
            cur.execute("insert into coins (id, name) values (%s, %s)", (i + 1, n))
        con.commit()


def insert_rates(con, dfs):
    with con.cursor() as cur:
        for i, df in enumerate(dfs.values()):
            for j in range(len(df)):
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
    with con.cursor() as cur:
        for i, (n, df) in enumerate(dfs.items()):
            cur.execute("select max(date) from rates join coins on rates.coin_id=coins.id where name=(%s)", (n))
            result = cur.fetchall()
            max_date = result[0]
            df_new = df[df['Date'] > list(max_date.values())[0]]
            for j in range(len(df_new)):
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('password', help='mysql password', type=str)
    parser.add_argument('db_name', help='database name', type=str)
    args = parser.parse_args()
    df_dict = read_dictionary()
    con, exists = create_connection(args.db_name, args.password)
    if exists:
        update_rates(con, df_dict)
    else:
        create_tables(con)
        insert_coins(con, df_dict)
        insert_rates(con, df_dict)



if __name__ == '__main__':
    main()
