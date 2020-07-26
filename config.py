# URL
HOMEPAGE = 'https://coinmarketcap.com/'
CURRENCIES_PAGE = 'https://coinmarketcap.com/currencies/'
CURRENCY_START = '/historical-data/?start=20130429&end='

# LOGGER
LOGGER_NAME = 'dmp.log'
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
CREATE_DICT = 'Creating dictionary...'
UPDATE_DICT = 'Updating dictionary...'
UPDATE_DB = 'Updating database...'
SAVE_DICT = 'Saving dictionary to file...'
CREATING_DB = 'Creating database...'
CON_DB = 'Attempting to connect to database'
CON_SUC = 'Connection successful'
CREATE_TABLES = 'Creating tables..'
COMPLETE = 'Complete'
UP_COINS = 'Updating coins...'
UP_RATES = 'Updating rates...'
UP_COINS_API = 'Updating coins from API...'
FETCH_API = 'Fetching data from api..'
SAVE_API = 'Saving api data to file...'
READ_DICT = 'Attempting to read dictionary...'
READ_API = 'Attempting to read api data...'
SUCCESS = 'Success' \
          ''
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


# MAGIC NUMBER
ZERO = 0
ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6

# EXCEPTION
REQ_FAIL = 'Request failed'
EMPTY_DF = 'Empty df created'
DATE_ERROR = 'Error reading dates from soup object for'
RATE_ERROR = 'Error reading rates from soup object for'
SOUP_ERROR = 'Error reading soup object for '
NO_DICT = 'Dictionary file not present in directory'
NO_API = 'api data file not present in directory'

# DATAFRAME
COMMA = ','
EMPTY = ''
DATE = 'Date'
OPEN = 'Open'
HIGH = 'High'
LOW = 'Low'
CLOSE = 'Close'
VOLUME = 'Volume'
CAP = 'Cap'
DF_DATE_FORMAT = '%b %d, %Y'
API_INTERVAL = 15
COIN = 'coin'
FR = 'fcas_rating'
FS = 'fcas_score'
DS = 'developer_score'
MMS = 'market_maturity_score'

# FILE
WB = 'wb'
RB = 'rb'
DICTIONARY_FILENAME = 'dfs_dict.p'
API_FILENAME = 'api_data.p'
API_key = ['YVL6KNC91W8WNDKE', 'WRZRQ8UPM5ZL95QV']


# Parser
ST = 'store_true'
UDB_HELP = 'Update mysql db'
CDICT_HELP = 'Create dictionary file'
UDICT_HELP = 'Update dictionary file'
UAPI_HELP = 'Create api file'
PASSWORD = 'password'
DB = 'db'
CDICT = '-cdict'
UDICT = '-udict'
UDB = '-udb'
CAPI = '-capi'
SPACE = '-'

# MYSQL STRING
NAME = 'name'
ID = 'id'
DATE_LOWER = 'date'


# MYSQL QUERY
CREATE_DB = 'create database'
CREATE_COINS = """create table coins (id int primary key auto_increment, 
                                      name char(255), 
                                      fcas_rating char(255), 
                                      fcas_score int, 
                                      dev_score int, 
                                      mm_score int)"""
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
INSERT_API = """update coins
                set 
                fcas_rating = %s, 
                fcas_score = %s, 
                dev_score = %s, 
                mm_score = %s  
                where name = %s """
