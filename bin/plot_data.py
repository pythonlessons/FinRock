import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Datasets/random_sinusoid.csv', index_col='timestamp', parse_dates=True)
df = df[['open', 'high', 'low', 'close']]
# limit to last 1000 data points
df = df[-1000:]

# plot the data
plt.figure(figsize=(10, 6))
plt.plot(df['close'])
plt.xlabel('Time')
plt.ylabel('Price')
plt.title('random_sinusoid.csv')
plt.grid(True)
plt.show()