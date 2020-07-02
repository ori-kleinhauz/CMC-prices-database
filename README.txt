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

In cases when the file is not present, or needs an update in your perspective, please choose yes ('y') when prompted by the program to update(create) the file.
otherwise, choose no ('n') to pick a currency and display its data

*** Be aware that every update of the database takes ~30 minutes to complete, due to limited requests\min the website allows (at least when using single IP for all requests).

enjoy!