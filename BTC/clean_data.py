from get_data import get_price_eb
import pandas as pd

def clean_data():
    price, eb = get_price_eb()
    df_price = pd.DataFrame(price, columns=['Date', 'Price'])
    df_eb = pd.DataFrame(eb, columns=['Date', 'EB'])
    df = pd.merge(df_price, df_eb, on='Date')
    df.index = pd.to_datetime(df['Date'], unit='ms')
    return df.drop(columns=['Date'])
    

if __name__ == "__main__":
    df = clean_data()
    
    if 1 == 0:
        # df.to_csv('Price_EB.csv')
        pass