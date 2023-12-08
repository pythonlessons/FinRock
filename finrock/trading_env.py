import typing
import numpy as np

from .state import State, Observations
from .data_feeder import PdDataFeeder
from .reward import simpleReward


class TradingEnv:
    def __init__(
            self,
            data_feeder: PdDataFeeder,
            output_transformer: typing.Callable = None,
            initial_balance: float = 1000.0,
            max_episode_steps: int = None,
            window_size: int = 50,
            reward_function: typing.Callable = simpleReward,
            metrics: typing.List[typing.Callable] = []
        ) -> None:
        self._data_feeder = data_feeder
        self._output_transformer = output_transformer
        self._initial_balance = initial_balance
        self._max_episode_steps = max_episode_steps if max_episode_steps is not None else len(data_feeder)
        self._window_size = window_size
        self._reward_function = reward_function
        self._metrics = metrics

        self._observations = Observations(window_size=window_size)
        self._observation_space = np.zeros(self.reset()[0].shape)
        self.action_space = 3

    @property
    def observation_space(self):
        return self._observation_space

    def _get_obs(self, index: int, balance: float=None) -> State:
        next_state = self._data_feeder[index]
        if balance is not None:
            next_state.balance = balance

        return next_state
    
    def _get_terminated(self):
        return False
        
    def _take_action(self, action: int, order_size: float) -> typing.Tuple[int, float]:
        # validate action is in range
        assert (action in list(range(self.action_space))) == True, f'action must be in range {self.action_space}, received: {action}'

        # get last state and next state
        last_state, next_state = self._observations[-2:]

        # modify action to hold (0) if we are out of balance
        if action == 2 and last_state.allocation_percentage == 1.0:
            action = 0

        # modify action to hold (0) if we are out of assets
        elif action == 1 and last_state.allocation_percentage == 0.0:
            action = 0

        if action == 2: # buy
            next_state.allocation_percentage = order_size
            next_state.assets = last_state.balance * order_size / last_state.close
            next_state.balance = last_state.balance - (last_state.balance * order_size)

        elif action == 1: # sell
            next_state.allocation_percentage = 0.0
            next_state.balance = last_state.assets * order_size * last_state.close
            next_state.assets = 0.0

        else: # hold
            next_state.allocation_percentage = last_state.allocation_percentage
            next_state.assets = last_state.assets
            next_state.balance = last_state.balance

        return action, order_size
    
    @property
    def metrics(self):
        return self._metrics

    def _metricsHandler(self, observation: State):
        metrics = {}
        # Loop through metrics and update
        for metric in self._metrics:
            metric.update(observation)
            metrics[metric.name] = metric.result

        return metrics

    def step(self, action: int) -> typing.Tuple[State, float, bool, bool, dict]:

        index = self._env_step_indexes.pop(0)

        observation = self._get_obs(index)
        # update observations object with new observation
        self._observations.append(observation)

        order_size = 1.0
        action, order_size = self._take_action(action, order_size)
        reward = self._reward_function(self._observations)
        terminated = self._get_terminated()
        truncated = False if self._env_step_indexes else True
        info = {
            "states": [observation],
            "metrics": self._metricsHandler(observation)
            }

        transformed_obs = self._output_transformer.transform(self._observations)

        return transformed_obs, reward, terminated, truncated, info

    def reset(self) -> typing.Tuple[State, dict]:
        """ Reset the environment and return the initial state
        """
        size = len(self._data_feeder) - self._max_episode_steps
        self._env_start_index = np.random.randint(0, size) if size > 0 else 0
        self._env_step_indexes = list(range(self._env_start_index, self._env_start_index + self._max_episode_steps))

        # Initial observations are the first states of the window size
        self._observations.reset()
        while not self._observations.full:
            self._observations.append(self._get_obs(self._env_step_indexes.pop(0), balance=self._initial_balance))

        info = {
            "states": self._observations.observations,
            "metrics": {}
            }
        
        # reset metrics with last state
        for metric in self._metrics:
            metric.reset(self._observations.observations[-1])

        transformed_obs = self._output_transformer.transform(self._observations)

        # return state and info
        return transformed_obs, info

    def render(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError