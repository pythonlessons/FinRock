import numpy as np
import pandas as pd
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
for gpu in tf.config.experimental.list_physical_devices('GPU'):
    tf.config.experimental.set_memory_growth(gpu, True)

from keras import layers, models

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv
from finrock.scalers import MinMaxScaler
from finrock.reward import simpleReward
from finrock.metrics import DifferentActions, AccountValue

from rockrl.utils.misc import MeanAverage
from rockrl.utils.memory import Memory
from rockrl.tensorflow import PPOAgent

df = pd.read_csv('Datasets/random_sinusoid.csv')
df = df[:-1000] # leave 1000 for testing

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


actor_model = models.Sequential([
    layers.Input(shape=input_shape, dtype=tf.float32),
    layers.Flatten(),
    layers.Dense(512, activation='elu'),
    layers.Dense(256, activation='elu'),
    layers.Dense(64, activation='elu'),
    layers.Dropout(0.5),
    layers.Dense(action_space, activation='softmax')
])

critic_model = models.Sequential([
    layers.Input(shape=input_shape, dtype=tf.float32),
    layers.Flatten(),
    layers.Dense(512, activation='elu'),
    layers.Dense(256, activation='elu'),
    layers.Dense(64, activation='elu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation=None)
])

agent = PPOAgent(
    actor = actor_model,
    critic = critic_model,
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.0002),
    batch_size=512,
    lamda=0.95,
    kl_coeff=0.5,
    c2=0.01,
    writer_comment='ppo_sinusoid',
)


memory = Memory()
meanAverage = MeanAverage(best_mean_score_episode=1000)
state, info = env.reset()
rewards = 0.0
while True:
    action, prob = agent.act(state)

    next_state, reward, terminated, truncated, info = env.step(action)
    memory.append(state, action, reward, prob, terminated, truncated, next_state, info)
    state = next_state

    if memory.done:
        history = agent.train(memory)
        mean_reward = meanAverage(np.sum(memory.rewards))

        if meanAverage.is_best(agent.epoch):
            agent.save_models('ppo_sinusoid')

        if history['kl_div'] > 0.05:
            agent.reduce_learning_rate(0.99, verbose=False)

        print(agent.epoch, np.sum(memory.rewards), mean_reward, info["metrics"]['account_value'], history['kl_div'])
        agent.log_to_writer(info['metrics'])
        memory.reset()
        state, info = env.reset()


        if agent.epoch >= 10000:
            break