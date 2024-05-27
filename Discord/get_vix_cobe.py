import datetime
import pandas as pd
import yfinance as yf

def get_closest_expiry_date(expiry_date_dict, current_date=None):
    if current_date is None:
        current_date = datetime.datetime.now().date()
    else:
        current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d').date()

    expiry_dates = sorted(expiry_date_dict.values())
    for date in expiry_dates:
        expiry_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        if expiry_date >= current_date:
            return expiry_date

    raise ValueError("No closest future expiry date found in the dictionary.")


def get_vixf_data(url):
    vixf_raw = pd.read_csv(url)
    return vixf_raw


def get_data(raw_df):
    vixf = pd.DataFrame({'VIXF':raw_df['Close'].to_list()}, index=pd.to_datetime(raw_df['Trade Date']))
    vix = yf.download('^VIX', start=vixf.index[0])
    spx = yf.download('^SPX', start=vixf.index[0])

    df = pd.concat([spx['Adj Close'].rename('SPX'),
                vix['Adj Close'].rename('VIX'),
                vixf['VIXF'].rename('VIXF')], axis=1)
    df = df.dropna()
    return df

def run():
    expiry_date_dict = {
        '2024-05': '2024-05-22',
        '2024-06': '2024-06-18',
        '2024-07': '2024-07-17',
        '2024-08': '2024-08-21',
        '2024-09': '2024-09-18',
        '2024-10': '2024-10-16',
        '2024-11': '2024-11-20',
        '2024-12': '2024-12-18'
        }
    
    closest_expiry_date = str(get_closest_expiry_date(expiry_date_dict))
    url = 'https://cdn.cboe.com/data/us/futures/market_statistics/historical_data/VX/VX_'+closest_expiry_date+'.csv'
    vixf_raw = get_vixf_data(url)
    df = get_data(vixf_raw)
    return df

if __name__ == '__main__':
    run()