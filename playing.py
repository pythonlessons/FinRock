import numpy as np
import pandas as pd

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv
from finrock.render import PygameRender
from finrock.scalers import MinMaxScaler
from finrock.reward import simpleReward

df = pd.read_csv('Datasets/random_sinusoid.csv')

pd_data_feeder = PdDataFeeder(df)


env = TradingEnv(
    data_feeder = pd_data_feeder,
    output_transformer = MinMaxScaler(min=pd_data_feeder.min, max=pd_data_feeder.max),
    initial_balance = 1000.0,
    max_episode_steps = 1000,
    window_size = 50,
    reward_function = simpleReward
)
action_space = env.action_space

pygameRender = PygameRender(frame_rate=60)


state, info = env.reset()
pygameRender.render(info)
rewards = 0.0
while True:
    # simulate model prediction, now use random action
    action = np.random.randint(0, action_space)
    # action = 0 # always hold

    state, reward, terminated, truncated, info = env.step(action)
    rewards += reward
    pygameRender.render(info)

    if terminated or truncated:
        print(info['states'][-1].account_value, rewards)
        rewards = 0.0
        state, info = env.reset()
        pygameRender.reset()