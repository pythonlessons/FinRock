import os
from datetime import datetime, timedelta
import time
import pandas as pd
import bitfinex

def download_data_to_csv(symbol, timeframe, limit):
    print(f"Downloading {symbol} {timeframe} data...")
    
    # Define the start date
    start_date = datetime(2018, 1, 1, 0, 0)
    start_date = int(time.mktime(start_date.timetuple()) * 1000)

    # Define the end date (current date and time)
    end_date = int(time.time() * 1000)
    # end_date = datetime(2020, 1, 1, 0, 0)
    # end_date = int(time.mktime(end_date.timetuple()) * 1000)
    #print(start_date, end_date)

    # Check if the CSV file exists and get the last datetime value
    csv_file_name = f"{symbol}_{timeframe}.csv"
    last_datetime = None

    if os.path.exists(csv_file_name):
        existing_data = pd.read_csv(csv_file_name, parse_dates=['Date'], date_parser=pd.to_datetime)
        if not existing_data.empty:
            last_datetime = existing_data['Date'].iloc[-1]

    if last_datetime:
        last_datetime = pd.to_datetime(last_datetime)
        next_datetime = last_datetime + timedelta(hours=1)
        last_timestamp = int(next_datetime.timestamp() * 1000)
        start_date = last_timestamp

    # Create api instance
    api_v2 = bitfinex.bitfinex_v2.api_v2()
    hour = 3600000  # 1 hour in milliseconds
    step = hour * limit
    data = []

    #print(start_date, end_date)

    while start_date < end_date:
        if start_date + step > end_date:
            step = end_date - start_date

        end = start_date + step
        data += api_v2.candles(symbol=symbol, interval=timeframe, limit=limit, start=start_date, end=end)

        # Convert timestamps to datetime objects for printing and formatting
        start_datetime = datetime.fromtimestamp(start_date / 1000)
        end_datetime = datetime.fromtimestamp(end / 1000)
        print(f"Downloaded data from {start_datetime} to {end_datetime}")

        start_date = end
        time.sleep(3)
        
    #print(data[:20])
    names = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']
    df = pd.DataFrame(data, columns=names)
    df.drop_duplicates(inplace=True)
    df['Date'] = pd.to_datetime(df['Date'], unit='ms')
    #df['Date'] = df['Date'].dt.strftime('%m-%d-%Y %H:%M')  # Format 'Date' as needed
    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)
    #print(str(df))

    # Append new data to the existing CSV file or create a new one if it doesn't exist
    if os.path.exists(csv_file_name):
        existing_data = pd.read_csv(csv_file_name)
        existing_data.set_index('Date', inplace=True)
        updated_data = pd.concat([existing_data, df])
        updated_data.to_csv(csv_file_name, index=True)  # Save the index along with the data
    else:
        df.to_csv(csv_file_name, index=True)  # If the file doesn't exist, save the index


symbol = 'ETHUSD'  # Example: Ethereum/US Dollar
timeframe = '1h'    # Fetch 1-hour candlestick data
limit = 1000           # Example: Number of data points to retrieve

download_data_to_csv(symbol, timeframe, limit)