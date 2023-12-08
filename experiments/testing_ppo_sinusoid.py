import numpy as np
import pandas as pd
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
for gpu in tf.config.experimental.list_physical_devices('GPU'):
    tf.config.experimental.set_memory_growth(gpu, True)

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv
from finrock.render import PygameRender
from finrock.scalers import MinMaxScaler
from finrock.reward import simpleReward
from finrock.metrics import DifferentActions, AccountValue


df = pd.read_csv('Datasets/random_sinusoid.csv')
df = df[-1000:]

pd_data_feeder = PdDataFeeder(df)

env = TradingEnv(
    data_feeder = pd_data_feeder,
    output_transformer = MinMaxScaler(min=pd_data_feeder.min, max=pd_data_feeder.max),
    initial_balance = 1000.0,
    max_episode_steps = 1000,
    window_size = 50,
    reward_function = simpleReward,
    metrics = [
        DifferentActions(),
        AccountValue(),
    ]
)

action_space = env.action_space
input_shape = env.observation_space.shape
pygameRender = PygameRender(frame_rate=120)

agent = tf.keras.models.load_model('runs/1701698276/ppo_sinusoid_actor.h5')

state, info = env.reset()
pygameRender.render(info)
rewards = 0.0
while True:
    # simulate model prediction, now use random action
    # action = np.random.randint(0, action_space)
    prob = agent.predict(np.expand_dims(state, axis=0), verbose=False)[0]
    action = np.argmax(prob)

    state, reward, terminated, truncated, info = env.step(action)
    rewards += reward
    pygameRender.render(info)

    if terminated or truncated:
        print(rewards, info["metrics"]['account_value'])
        state, info = env.reset()
        rewards = 0.0
        pygameRender.reset()
        pygameRender.render(info)