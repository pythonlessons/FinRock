import numpy as np
import pandas as pd
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
for gpu in tf.config.experimental.list_physical_devices('GPU'):
    tf.config.experimental.set_memory_growth(gpu, True)

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv
from finrock.render import PygameRender


df = pd.read_csv('Datasets/random_sinusoid.csv')
df = df[-1000:]

model_path = "runs/1704798174"

pd_data_feeder = PdDataFeeder.load_config(df, model_path)
env = TradingEnv.load_config(pd_data_feeder, model_path)

action_space = env.action_space
input_shape = env.observation_space.shape
pygameRender = PygameRender(frame_rate=120)

agent = tf.keras.models.load_model(f'{model_path}/ppo_sinusoid_actor.h5')

state, info = env.reset()
pygameRender.render(info)
rewards = 0.0
while True:
    # simulate model prediction, now use random action
    action = agent.predict(np.expand_dims(state, axis=0), verbose=False)[0][:-1]

    state, reward, terminated, truncated, info = env.step(action)
    rewards += reward
    pygameRender.render(info)

    if terminated or truncated:
        print(rewards)
        for metric, value in info['metrics'].items():
            print(metric, value)
        state, info = env.reset()
        rewards = 0.0
        pygameRender.reset()
        pygameRender.render(info)