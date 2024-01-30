import numpy as np
import pandas as pd
import tensorflow as tf
tf.get_logger().setLevel('ERROR')
for gpu in tf.config.experimental.list_physical_devices('GPU'):
    tf.config.experimental.set_memory_growth(gpu, True)

from keras import layers, models

from finrock.data_feeder import PdDataFeeder
from finrock.trading_env import TradingEnv, ActionSpace
from finrock.scalers import ZScoreScaler
from finrock.reward import AccountValueChangeReward
from finrock.metrics import DifferentActions, AccountValue, MaxDrawdown, SharpeRatio
from finrock.indicators import BolingerBands, RSI, PSAR, SMA, MACD

from rockrl.utils.misc import MeanAverage
from rockrl.utils.memory import MemoryManager
from rockrl.tensorflow import PPOAgent
from rockrl.utils.vectorizedEnv import VectorizedEnv

df = pd.read_csv('Datasets/random_sinusoid.csv')
df = df[:-1000] # leave 1000 for testing

pd_data_feeder = PdDataFeeder(
    df,
    indicators = [
        BolingerBands(data=df, period=20, std=2),
        RSI(data=df, period=14),
        PSAR(data=df),
        MACD(data=df),
        SMA(data=df, period=7),
    ]
)

num_envs = 10
env = VectorizedEnv(
    env_object = TradingEnv,
    num_envs = num_envs,
    data_feeder = pd_data_feeder,
    output_transformer = ZScoreScaler(),
    initial_balance = 1000.0,
    max_episode_steps = 1000,
    window_size = 50,
    reward_function = AccountValueChangeReward(),
    action_space = ActionSpace.CONTINUOUS,
    metrics = [
        DifferentActions(),
        AccountValue(),
        MaxDrawdown(),
        SharpeRatio(),
    ]
)

action_space = env.action_space
input_shape = env.observation_space.shape


def actor_model(input_shape, action_space):
    input = layers.Input(shape=input_shape, dtype=tf.float32)
    x = layers.Flatten()(input)
    x = layers.Dense(512, activation='elu')(x)
    x = layers.Dense(256, activation='elu')(x)
    x = layers.Dense(64, activation='elu')(x)
    x = layers.Dropout(0.2)(x)
    action = layers.Dense(action_space, activation="tanh")(x)
    sigma = layers.Dense(action_space)(x)
    sigma = layers.Dense(1, activation='sigmoid')(sigma)
    output = layers.concatenate([action, sigma]) # continuous action space
    return models.Model(inputs=input, outputs=output)

def critic_model(input_shape):
    input = layers.Input(shape=input_shape, dtype=tf.float32)
    x = layers.Flatten()(input)
    x = layers.Dense(512, activation='elu')(x)
    x = layers.Dense(256, activation='elu')(x)
    x = layers.Dense(64, activation='elu')(x)
    x = layers.Dropout(0.2)(x)
    output = layers.Dense(1, activation=None)(x)
    return models.Model(inputs=input, outputs=output)


agent = PPOAgent(
    actor = actor_model(input_shape, action_space),
    critic = critic_model(input_shape),
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.00005),
    batch_size=128,
    lamda=0.95,
    kl_coeff=0.5,
    c2=0.01,
    writer_comment='ppo_sinusoid',
    action_space="continuous",
)
pd_data_feeder.save_config(agent.logdir)
env.env.save_config(agent.logdir)

memory = MemoryManager(num_envs=num_envs)
meanAverage = MeanAverage(best_mean_score_episode=1000)
states, infos = env.reset()
rewards = 0.0
while True:
    action, prob = agent.act(states)

    next_states, reward, terminated, truncated, infos = env.step(action)
    memory.append(states, action, reward, prob, terminated, truncated, next_states, infos)
    states = next_states

    for index in memory.done_indices():
        env_memory = memory[index]
        history = agent.train(env_memory)
        mean_reward = meanAverage(np.sum(env_memory.rewards))

        if meanAverage.is_best(agent.epoch):
            agent.save_models('ppo_sinusoid')

        if history['kl_div'] > 0.2 and agent.epoch > 1000:
            agent.reduce_learning_rate(0.995, verbose=False)

        info = env_memory.infos[-1]
        print(agent.epoch, np.sum(env_memory.rewards), mean_reward, info["metrics"]['account_value'], history['kl_div'])
        agent.log_to_writer(info['metrics'])
        states[index], infos[index] = env.reset(index=index)

    if agent.epoch >= 20000:
        break

env.close()
exit()