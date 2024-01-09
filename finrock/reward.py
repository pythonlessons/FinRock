import numpy as np
from .state import Observations

class Reward:
    def __init__(self) -> None:
        pass

    @property
    def __name__(self) -> str:
        return self.__class__.__name__
    
    def __call__(self, observations: Observations) -> float:
        raise NotImplementedError
    
    def reset(self, observations: Observations):
        pass
    

class SimpleReward(Reward):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, observations: Observations) -> float:
        assert isinstance(observations, Observations) == True, "observations must be an instance of Observations"

        last_state, next_state = observations[-2:]

        # buy
        if next_state.allocation_percentage > last_state.allocation_percentage:
            # check whether it was good or bad to buy
            order_size = next_state.allocation_percentage - last_state.allocation_percentage
            reward = (next_state.close - last_state.close) / last_state.close * order_size
            hold_reward = (next_state.close - last_state.close) / last_state.close * last_state.allocation_percentage
            reward += hold_reward

        # sell
        elif next_state.allocation_percentage < last_state.allocation_percentage:
            # check whether it was good or bad to sell
            order_size = last_state.allocation_percentage - next_state.allocation_percentage
            reward = -1 * (next_state.close - last_state.close) / last_state.close * order_size
            hold_reward = (next_state.close - last_state.close) / last_state.close * next_state.allocation_percentage
            reward += hold_reward

        # hold
        else:
            # check whether it was good or bad to hold
            ratio = -1 if not last_state.allocation_percentage else last_state.allocation_percentage
            reward = (next_state.close - last_state.close) / last_state.close * ratio
            
        return reward

class AccountValueChangeReward(Reward):
    def __init__(self) -> None:
        super().__init__()
        self.ratio_days=365.25

    def reset(self, observations: Observations):
        super().reset(observations)
        self.returns = []
    
    def __call__(self, observations: Observations) -> float:
        assert isinstance(observations, Observations) == True, "observations must be an instance of Observations"

        last_state, next_state = observations[-2:]
        reward = (next_state.account_value - last_state.account_value) / last_state.account_value

        return reward