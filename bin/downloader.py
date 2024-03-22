import os
from datetime import datetime, timedelta
import time
import pandas as pd
import requests

def download_data_to_csv(symbol, timeframe, limit):
    print(f"Downloading {symbol} {timeframe} data...")
    
    start_date = datetime(2018, 1, 1, 0, 0)
    start_date = int(time.mktime(start_date.timetuple()) * 1000)

    end_date = int(time.time() * 1000)

    csv_file_name = f'Datasets/random_sinusoid.csv'
    last_datetime = None

    if os.path.exists(csv_file_name):
        existing_data = pd.read_csv(csv_file_name, parse_dates=['timestamp'])
        if not existing_data.empty:
            last_datetime = existing_data['timestamp'].iloc[-1]

    if last_datetime:
        last_datetime = pd.to_datetime(last_datetime)
        next_datetime = last_datetime + timedelta(hours=4)
        # next_datetime = last_datetime + timedelta(minutes=1)
        last_timestamp = int(next_datetime.timestamp() * 1000)
        start_date = last_timestamp

    hour = 14400000  # 4 hour in milliseconds
    step = hour * limit
    data = []

    while start_date < end_date:
        if start_date + step > end_date:
            step = end_date - start_date

        end = start_date + step
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:t{symbol}/hist?start={start_date}&end={end}&limit={limit}"
        response = requests.get(url)
        data += response.json()

        start_datetime = datetime.fromtimestamp(start_date / 1000)
        end_datetime = datetime.fromtimestamp(end / 1000)
        print(f"Downloaded data from {start_datetime} to {end_datetime}")

        start_date = end
        time.sleep(3)
        
    names = ['timestamp', 'open', 'close', 'high', 'low', 'volume']
    df = pd.DataFrame(data, columns=names)
    df.drop_duplicates(inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.sort_values('timestamp', inplace=True)
    df = df[['timestamp', 'open', 'high', 'low', 'close']]  # Reorder the columns
    df.reset_index(drop=True, inplace=True)  # Reset the index
   # df.index = df.index[::-1]  # Reverse the index

    if os.path.exists(csv_file_name):
        existing_data = pd.read_csv(csv_file_name, index_col=0)
        updated_data = pd.concat([existing_data, df], ignore_index=True)
        updated_data.to_csv(csv_file_name, index=True, header=True)
    else:
        df.to_csv(csv_file_name, index=True, header=True)


symbol = 'ETHUSD'  # Example: Ethereum/US Dollar
timeframe = '4H'    # Fetch 4-hour candlestick data
limit = 1000           # Number of data points to retrieve

download_data_to_csv(symbol, timeframe, limit)
