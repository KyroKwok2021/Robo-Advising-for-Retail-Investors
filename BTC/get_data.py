import requests
import time


def fetch_data(url, params, headers, cookies=None):
    response = requests.get(url, params=params, headers=headers, cookies=cookies)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")


def get_price(params, headers):
    price_base_url = "https://live-api.cryptoquant.com/api/v2/assets/61712eb35a176168a02409e8/price"
    return fetch_data(price_base_url, params, headers)


def get_eb(params, headers):
    eb_base_url = "https://live-api.cryptoquant.com/api/v3/charts/61a5fb0c45de34521f1dcaad"
    return fetch_data(eb_base_url, params, headers)


def get_price_eb():

    current_timestamp = int(time.time() * 1000)
    params = {
        'window': 'DAY',
        'from': 0,
        'to': 1713312000000,
        'limit': 70000
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    price = get_price(params, headers)['data']
    eb = get_eb(params, headers)['result']['data']

    return (price, eb)

if __name__ == "__main__":
    get_price_eb()
