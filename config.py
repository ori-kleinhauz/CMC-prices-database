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
                                'or create it by choosing "y" for updating the database'}
DICTIONARY_NAME = 'dict.data'