import pymysql.cursors
import numpy as np
from ms1 import read_dictionary

pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)

con = pymysql.connect(host='localhost',
                             user='root',
                             password='sql420',
                             charset='utf8mb4',
                             database='cmc',
                             cursorclass=pymysql.cursors.DictCursor)
DB_FILENAME = 'cmc'
dfs = read_dictionary()

with con.cursor() as cur:
    cur.execute(f"create database {DB_FILENAME}")

# with con.cursor() as cur:
#     cur.execute("drop table coins")

with con.cursor() as cur:
    cur.execute("create table coins (id int primary key, currency char(255))")

with con.cursor() as cur:
    for i in range(len(dfs.keys())):
        cur.execute("insert into coins (id, currency) values (%s,%s)", (i, list(dfs.keys())[i]))
    con.commit()


# with con.cursor() as cur:
    # cur.execute("drop table rates")

with con.cursor() as cur:
    cur.execute("""create table rates
    (id int primary key auto_increment, coin_id int, date date, open float, high float, close float, volume float, cap float,
    foreign key (coin_id) references coins(id))""")

with con.cursor() as cur:
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









