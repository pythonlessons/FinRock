import numpy as np
import pandas as pd

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv
from finrock.render import PygameRender

df = pd.read_csv('Datasets/random_sinusoid.csv')

pd_data_feeder = PdDataFeeder(df)

env = TradingEnv(
    data_feeder = pd_data_feeder,
    max_episode_steps = 1000
)
action_space = env.action_space

pygameRender = PygameRender(frame_rate=10)


state, info = env.reset()
pygameRender.render(info)
while True:
    # simulate model prediction, now use random action
    action = np.random.randint(0, action_space)

    state, reward, terminated, truncated, info = env.step(action)
    pygameRender.render(info)

    if terminated or truncated:
        state, info = env.reset()
        pygameRender.reset()