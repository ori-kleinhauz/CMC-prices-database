Authors:
Ori Kleinhauz
Yuval Herman

Files in repository
ms1.py - python script
data.dict - database
requirements.txt

Description:
This project offers complete historical access to worldwide average prices of the 100 highest traded crypto currencies (listed by market cap), according to http://www.coinmarketcap.com (hereinafter: the website).

This project uses scrapping technics to collect its data, NOT based upon any kind of API provider, neither free nor otherwise.
This is naturally great news to anyone wishes to built a 100 crypto currencies historical database on his own machine/server.

Notifications:
As default, the program searches for the file 'dict.data' in the project's directory and offers historical rates per the user's input from it.

In cases when the file is not present - either because you didn't clone it / deleted it / the file needs an update in your perspective :
a deviation from default operations in required as follows --> you are required to uncomment the following functions at the first run of the program :
1. update_all_coins_data(get_100_currencies())
2. create_dictionary()
both functions are currently commented and are located in main().
please remember to re-comment these functions after database finished the update/built.

*** Be aware that every update of the database takes 25 minutes to complete, due to limited requests\min the website allowes (at least when using single IP for all requests).

enjoy!



