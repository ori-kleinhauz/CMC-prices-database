Authors:
Ori Kleinhauz
Yuval Herman

Files in this repository:
ms1.py - main script file
api.py - connection with free api from https://www.alphavantage.com - getting community ratings on Coins. (requires personal free key added to config file)
digital_currency_list.csv - contains intermediate between scraped Coin names to API Coin names.
MySQL_DB.py - class object for storing database locally and execute commands.
config.py - constants, magic numbers, queries, name fields, sleep intervals.
dfs_dict.p - scraped data kept in binary format.
api_data.p - api data kept in binary format.
requirements.txt - deployment of environment dependencies (pip install -r requirements.txt).
DMP-MS2_ERD.pdf - relationship diagram of mysql database.


Description:
This project offers access to complete historical data of worldwide daily average rates for the top 100 traded
crypto currencies sorted by market capitalization according to http://www.coinmarketcap.com 

It utilizes both original scraping techniques and a public API to collect data.

The project is operated as follows:

Run "python ms1.py" with either of the following arguments:

  -cdict, --cdict   Create dictionary file
  -capi, --capi     Create api file
  -udict, --udict   Update dictionary file
  -udb password db  Update mysql db


At first activation, please create the database locally using:

 1. -cdict  creates the database and saved locally
 2. -capi   creates the ratings and saved locally

(*) These commands shall take about 15 minutes each due to the limitations imposed by the sleep intervals required for successful scraping & API operations.

Add new currencies if any, to the local database using:

 3. -udict   updates the local database dfs_dict.p if the top 100 currencies list on the website was changed.

Upstream the databases to a mysql database using:

 4. -udb     with added parameters (password, database desired name), creates or updates the database.


Enjoy!
