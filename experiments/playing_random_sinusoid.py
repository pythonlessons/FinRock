import numpy as np
import pandas as pd

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv
from finrock.render import PygameRender
from finrock.scalers import ZScoreScaler
from finrock.reward import AccountValueChangeReward
from finrock.indicators import BolingerBands, SMA, RSI, PSAR, MACD
from finrock.metrics import DifferentActions, AccountValue, MaxDrawdown, SharpeRatio

df = pd.read_csv('Datasets/random_sinusoid.csv')

pd_data_feeder = PdDataFeeder(
    df = df,
    indicators = [
        BolingerBands(data=df, period=20, std=2),
        RSI(data=df, period=14),
        PSAR(data=df),
        MACD(data=df),
        SMA(data=df, period=7),
    ]
)

env = TradingEnv(
    data_feeder = pd_data_feeder,
    output_transformer = ZScoreScaler(),
    initial_balance = 1000.0,
    max_episode_steps = 1000,
    window_size = 50,
    reward_function = AccountValueChangeReward(),
    metrics = [
        DifferentActions(),
        AccountValue(),
        MaxDrawdown(),
        SharpeRatio(),
    ]
)
action_space = env.action_space
input_shape = env.observation_space.shape

env.save_config()

pygameRender = PygameRender(frame_rate=60)

state, info = env.reset()
pygameRender.render(info)
rewards = 0.0
while True:
    # simulate model prediction, now use random action
    action = np.random.randint(0, action_space)

    state, reward, terminated, truncated, info = env.step(action)
    rewards += reward
    pygameRender.render(info)

    if terminated or truncated:
        print(info['states'][-1].account_value, rewards)
        rewards = 0.0
        state, info = env.reset()
        pygameRender.reset()