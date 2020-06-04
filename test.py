import requests
r = requests.get('https://coinmarketcap.com/currencies/bitcoin/historical-data/?start=20130429&end=20200604')
print(r.status_code)
