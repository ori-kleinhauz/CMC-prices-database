from ms1 import read_dictionary_from_pickle
import requests
import pandas as pd
import config
from time import sleep
from tqdm import tqdm


def get_api_data():
    """
    added is a csv file of 500+ coin names and symbol that the API requires
    in its http call to be added.
    it is added to the project because the script matches between scrapped database names to API names"""
    df = pd.DataFrame
    try:
        df = pd.read_csv('digital_currency_list.csv')
    except:
        FileNotFoundError('cant located digital_currency_list.csv in project directory')
        exit()
    api_key1 = 'YVL6KNC91W8WNDKE'
    api_key2 = 'WRZRQ8UPM5ZL95QV'

    """
    this API allows us in free trial mode - only 5 calls per minute.
    Therefore, 12 seconds sleep interval between call period """

    d_class = read_dictionary_from_pickle()
    symbols = {}
    for key in list(d_class.keys()):
        if key in df['currency name'].values:
            symbols[key] = df[df['currency name'] == key]['currency code'].values[0]

    SLEEP_INT = config.API_INTERVAL
    df_api = pd.DataFrame(columns=['coin', 'fcas_rating', 'fcas_score', 'developer_score', 'market_maturity_score'])

    ''' making API calls to retrieve data from web   ===> SLEEP_INT * calls = time this would take'''

    for x, (key, value) in enumerate(tqdm(symbols.items())):
        querystring = {"symbol": value, "function": "CRYPTO_RATING"}
        if x % 2 == 0:
            api_key = api_key1
        else:
            api_key = api_key2
        url = f'https://www.alphavantage.co/query?function={querystring["function"]}&symbol=' \
              f'{querystring["symbol"]}&apikey={api_key}'
        headers = {'x-rapidapi-host': "alpha-vantage.p.rapidapi.com",
                   'x-rapidapi-key': "712a7be151msh49c200d2095f135p1aeae2jsn864918dad2ed"}
        try:
            response = requests.request("GET", url, headers=headers)
            json = response.json()['Crypto Rating (FCAS)']
            fcas_rating, fcas_score, developer_score, market_maturity_score = \
                json["3. fcas rating"], json["4. fcas score"], json["5. developer score"], json["6. market maturity score"]
            df_api.loc[x] = [key, fcas_rating, fcas_score, developer_score, market_maturity_score]
            print(df_api.loc[x])
            sleep(SLEEP_INT)
        except Exception as E:
            print(E)
    return df_api


if __name__ == '__main__':
    df = get_api_data()
    print(df)