import typing
import numpy as np

from .state import State
from .data_feeder import PdDataFeeder

class TradingEnv:
    def __init__(
            self,
            data_feeder: PdDataFeeder,
            max_episode_steps: int = None
        ) -> None:
        self._data_feeder = data_feeder
        self._max_episode_steps = max_episode_steps if max_episode_steps is not None else len(data_feeder)
        self.action_space = 3

    def _get_obs(self, index) -> State:
        return self._data_feeder[index]
    
    def _get_terminated(self):
        return False
    
    def _get_reward(self):
        return 0.0

    def step(self, action: int) -> typing.Tuple[State, float, bool, bool, dict]:

        index = self._env_step_indexes.pop(0)

        observation = self._get_obs(index)
        reward = self._get_reward()
        terminated = self._get_terminated()
        truncated = False if self._env_step_indexes else True
        info = {"states": [observation]}

        return observation, reward, terminated, truncated, info

    def reset(self) -> typing.Tuple[State, dict]:
        size = len(self._data_feeder) - self._max_episode_steps
        self._env_start_index = np.random.randint(0, size) if size > 0 else 0
        self._env_step_indexes = list(range(self._env_start_index, self._env_start_index + self._max_episode_steps))

        index = self._env_step_indexes.pop(0)

        observation = self._get_obs(index)
        info = {"states": [observation]}

        # return state and info
        return observation, info

    def render(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError