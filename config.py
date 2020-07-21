# URL
HOMEPAGE = 'https://coinmarketcap.com/'
CURRENCIES_PAGE = 'https://coinmarketcap.com/currencies/'
CURRENCY_START = '/historical-data/?start=20130429&end='

# SCRAPER
SLEEP_INTERVAL = 5
HTML_PARSER = 'html.parser'
A = 'a'
CMC_LINK = 'cmc-link'
CURRENCIES = 'currencies'
HREF = 'href'
SLASH = '/'
TITLE = 'title'
CURR_DATE_FORMAT = '%Y%m%d'
TD = 'td'
CMC_RIGHT = 'cmc-table__cell cmc-table__cell--right'
CMC_LEFT = 'cmc-table__cell cmc-table__cell--sticky cmc-table__cell--left'
COMMA = ','
EMPTY = ''

# MAGIC NUMBER
ZERO = 0
ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6

# EXCEPTION
REQ_FAIL = 'request failed'
EMPTY_DF = 'empty df created'

# DATAFRAME
DATE = 'Date'
OPEN = 'Open'
HIGH = 'High'
LOW = 'Low'
CLOSE = 'Close'
VOLUME = 'Volume'
CAP = 'Cap'
DF_DATE_FORMAT = '%b %d, %Y'

# FILE
WB = 'wb'
RB = 'rb'
DICTIONARY_FILENAME = 'dfs_dict.p'

# MYSQL STRING
NAME = 'name'
ID = 'id'
DATE_LOWER = 'date'

# MYSQL QUERY
CREATE_DB = 'create database'
CREATE_COINS = 'create table coins (id int primary key auto_increment, name char(255))'
CREATE_RATES = """create table rates
                            (id int primary key auto_increment, 
                            coin_id int, 
                            date date, 
                            open float, 
                            high float, 
                            low float,
                            close float, 
                            volume float, 
                            cap float,
                            foreign key (coin_id) references coins(id))"""
SELECT_NAME = 'select name from coins'
INSERT_COINS = 'insert into coins (name) values (%s)'
INSERT_RATES = """insert into rates (coin_id, date, open, high, low,  close, volume, cap)
                                     values (%s, %s, %s, %s, %s, %s, %s, %s)"""
SELECT_ID = 'select id from coins where name=(%s)'
SELECT_DATES = 'select distinct(date) from rates where coin_id = (%s)'
