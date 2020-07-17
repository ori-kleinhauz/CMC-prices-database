HOMEPAGE = 'https://coinmarketcap.com/'
CURRENCIES_PAGE = 'https://coinmarketcap.com/currencies/'
CURRENCY_START = '/historical-data/?start=20130429&end='
SLEEP_INTERVAL = 15
PICKLE_FOLDER = 'pickles'
COL_NAMES = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Cap']
ERRORS_MESSAGES = {'Connection_failed': 'error locating {coin} data. check possible name mismatch on CMC',
                   'read_soup': 'Error reading soup object from {coin} file',
                   'read_dates': 'Error reading dates from soup object for {coin}',
                   'create_dict': 'Error creating dictionary from temporary pickle files',
                   'delete_pickles': 'Directory not found / could not delete folder',
                   'read_dictionary': 'Dictionary file not present in the current folder!,'
                                      'make sure to download it from github repository, '
                                      'or create it by choosing "y" for updating the database',
                   'read_class': 'class object does not exist'}
DICTIONARY_NAME = 'dict.data'
CREATE_TABLE_DATES = "create table coins (id int primary key auto_increment, name char(255))"
CREATE_TABLE_RATES = """create table rates
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
INSERT_NEW_COIN = "insert into coins (name) values (%s)"
INSERT_NEW_RATE = "insert into rates (coin_id, date, open, high, low,  close, volume, cap) " \
                  "values (%s, %s, %s, %s, %s, %s, %s, %s)"
GET_MAX_DATE_IN_DB = "select max(date) from rates join coins on rates.coin_id=coins.id where name=(%s)"
GET_COIN_ID_IN_DB = "select id from coins where name=(%s)"
