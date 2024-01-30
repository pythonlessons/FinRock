import os
import json
import typing
import importlib
import numpy as np

from enum import Enum
from .state import State, Observations
from .data_feeder import PdDataFeeder
from .reward import SimpleReward

class ActionSpace(Enum):
    DISCRETE = 3
    CONTINUOUS = 2

class TradingEnv:
    def __init__(
            self,
            data_feeder: PdDataFeeder,
            output_transformer: typing.Callable = None,
            initial_balance: float = 1000.0,
            max_episode_steps: int = None,
            window_size: int = 50,
            reward_function: typing.Callable = SimpleReward(),
            action_space: ActionSpace = ActionSpace.DISCRETE,
            metrics: typing.List[typing.Callable] = [],
            order_fee_percent: float = 0.001
        ) -> None:
        self._data_feeder = data_feeder
        self._output_transformer = output_transformer
        self._initial_balance = initial_balance
        self._max_episode_steps = max_episode_steps if max_episode_steps is not None else len(data_feeder)
        self._window_size = window_size
        self._reward_function = reward_function
        self._metrics = metrics
        self._order_fee_percent = order_fee_percent

        self._observations = Observations(window_size=window_size)
        self._observation_space = np.zeros(self.reset()[0].shape)
        self._action_space = action_space
        self.fee_ratio = 1 - self._order_fee_percent

    @property
    def action_space(self):
        return self._action_space.value

    @property
    def observation_space(self):
        return self._observation_space

    def _get_obs(self, index: int, balance: float=None) -> State:
        next_state = self._data_feeder[index]
        if next_state is None:
            return None

        if balance is not None:
            next_state.balance = balance

        return next_state
    
    def _get_terminated(self):
        return False
        
    def _take_action(self, action_pred: typing.Union[int, np.ndarray]) -> typing.Tuple[int, float]:
        """
        """
        # validate action is in range

        if isinstance(action_pred, np.ndarray):
            order_size = np.clip(action_pred[1], 0, 1)
            order_size = np.around(order_size, decimals=2)
            action = int((np.clip(action_pred[0], -1, 1) + 1) * 1.5) # scale from -1,1 to 0,3
        elif action_pred in [0, 1, 2]:
            order_size = 1.0
            action = action_pred
            assert (action in list(range(self._action_space.value))) == True, f'action must be in range {self._action_space.value}, received: {action}'
        else:
            raise ValueError(f'invalid action type: {type(action)}')


        # get last state and next state
        last_state, next_state = self._observations[-2:]

        # modify action to hold (0) if we are out of balance
        if action == 2 and last_state.allocation_percentage == 1.0:
            action = 0

        # modify action to hold (0) if we are out of assets
        elif action == 1 and last_state.allocation_percentage == 0.0:
            action = 0

        if order_size == 0:
            action = 0

        if action == 2: # buy
            buy_order_size = order_size
            next_state.allocation_percentage = last_state.allocation_percentage + (1 - last_state.allocation_percentage) * buy_order_size
            next_state.assets = last_state.assets + (last_state.balance * buy_order_size / last_state.close) * self.fee_ratio
            next_state.balance = last_state.balance - (last_state.balance * buy_order_size) * self.fee_ratio

        elif action == 1: # sell
            sell_order_size = order_size
            next_state.allocation_percentage = last_state.allocation_percentage - last_state.allocation_percentage * sell_order_size
            next_state.balance = last_state.balance + (last_state.assets * sell_order_size * last_state.close) * self.fee_ratio
            next_state.assets = last_state.assets - (last_state.assets * sell_order_size) * self.fee_ratio

        else: # hold
            next_state.allocation_percentage = last_state.allocation_percentage
            next_state.assets = last_state.assets
            next_state.balance = last_state.balance

        if next_state.allocation_percentage > 1.0:
            raise ValueError(f'next_state.allocation_percentage > 1.0: {next_state.allocation_percentage}')
        elif next_state.allocation_percentage < 0.0:
            raise ValueError(f'next_state.allocation_percentage < 0.0: {next_state.allocation_percentage}')

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

        action, order_size = self._take_action(action)
        reward = self._reward_function(self._observations)
        terminated = self._get_terminated()
        truncated = False if self._env_step_indexes else True
        info = {
            "states": [observation],
            "metrics": self._metricsHandler(observation)
            }

        transformed_obs = self._output_transformer.transform(self._observations)

        if np.isnan(transformed_obs).any():
            raise ValueError("transformed_obs contains nan values, check your data")

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
            obs = self._get_obs(self._env_step_indexes.pop(0), balance=self._initial_balance)
            if obs is None:
                continue
            # update observations object with new observation
            self._observations.append(obs)

        info = {
            "states": self._observations.observations,
            "metrics": {}
            }
        
        # reset metrics with last state
        for metric in self._metrics:
            metric.reset(self._observations.observations[-1])

        transformed_obs = self._output_transformer.transform(self._observations)
        if np.isnan(transformed_obs).any():
            raise ValueError("transformed_obs contains nan values, check your data")
        
        # return state and info
        return transformed_obs, info

    def render(self):
        raise NotImplementedError

    def close(self):
        """ Close the environment
        """
        pass

    def config(self):
        """ Return the environment configuration
        """
        return {
            "data_feeder": self._data_feeder.__name__,
            "output_transformer": self._output_transformer.__name__,
            "initial_balance": self._initial_balance,
            "max_episode_steps": self._max_episode_steps,
            "window_size": self._window_size,
            "reward_function": self._reward_function.__name__,
            "metrics": [metric.__name__ for metric in self._metrics],
            "order_fee_percent": self._order_fee_percent,
            "observation_space_shape": tuple(self.observation_space.shape),
            "action_space": self._action_space.name,
        }
    
    def save_config(self, path: str = ""):
        """ Save the environment configuration
        """
        output_path = os.path.join(path, "TradingEnv.json")
        with open(output_path, "w") as f:
            json.dump(self.config(), f, indent=4)

    @staticmethod
    def load_config(data_feeder, path: str = "", **kwargs):
        """ Load the environment configuration
        """

        input_path = os.path.join(path, "TradingEnv.json")
        if not os.path.exists(input_path):
            raise Exception(f"TradingEnv Config file not found in {path}")
        with open(input_path, "r") as f:
            config = json.load(f)

        environment = TradingEnv(
            data_feeder = data_feeder,
            output_transformer = getattr(importlib.import_module(".scalers", package=__package__), config["output_transformer"])(),
            initial_balance = kwargs.get("initial_balance") or config["initial_balance"],
            max_episode_steps = kwargs.get("max_episode_steps") or config["max_episode_steps"],
            window_size = kwargs.get("window_size") or config["window_size"],
            reward_function = getattr(importlib.import_module(".reward", package=__package__), config["reward_function"])(),
            action_space = ActionSpace[config["action_space"]],
            metrics = [getattr(importlib.import_module(".metrics", package=__package__), metric)() for metric in config["metrics"]],
            order_fee_percent = kwargs.get("order_fee_percent") or config["order_fee_percent"]
        )
        
        return environment