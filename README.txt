Authors:
Ori Kleinhauz
Yuval Herman

Files in this repository:
ms1.py - python script for scraping coin data and saving it to a binary file in the projects directory.
ms2.py - python script for deploying all coin database to a mysql server for easier managment.
DMP-MS2_ERD.pdf - decription of the sql database structure.
data.dict - database in binary mode.
requirements.txt
config.py


Description:
This project offers complete historical access to worldwide average prices of the 100 highest traded crypto currencies (listed by market cap), according to http://www.coinmarketcap.com (hereinafter: the website).

This project uses scrapping technics to collect its data, NOT based upon any kind of API provider, neither free nor otherwise.
This is naturally great news to anyone wishes to built a 100 crypto currencies historical database on his own machine/server.

Notifications:
The script offers a variety of command line options:

usage: ms1.py [-h] [-c] [-u] [-u_db password DB] [-price coin date] [-all_prices coin] [-last_date] [-coin_b_dates coin begin end]

optional arguments:
  -h, --help                    show this help message and exit
  -c, --c                       show available coins
  -u, --u                       Update Database locally
  -u_db password DB             Update mysql DB
  -price coin date              get coin value by date
  -all_prices coin              get all coin history
  -last_date                    get last date in database
  -coin_b_dates coin begin end  get coin last date in database


As default, the script requires arguments using the command line interface in order to work according to users requirements.
It can operate on both small scale local machine - creates local class object to answer all types of Coin queries,
as well as creating and updating a server side mysql database copy .

-u: scrape, and load to class object all 100 coin data (-u)

-u_db: copy all data to a mysql database (-u_db, password, Database name)

-price: use this argument to get a coin value per date supplied (-price, coin, date)

-all_prices: use this argument to get all values of a coin's history (-all_prices, coin)

-last_date: use this argument to get the last date the database (local class object) is updated (-last_date)

-coin_b_dates: use this argument to get the values of a coin supplied between two dates (-coin_b_dates, coin, bgein, end)



enjoy!
