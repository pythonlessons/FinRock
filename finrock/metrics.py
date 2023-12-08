from .state import State

""" Metrics are used to track and log information about the environment.
possible metrics:
- DifferentActions,
- AccountValue, 
- MaxDrawdown, 
- SharpeRatio, 
- AverageProfit, 
- AverageLoss, 
- AverageTrade, 
- WinRate, 
- LossRate, 
- AverageWin, 
- AverageLoss,
- AverageWinLossRatio, 
- AverageTradeDuration, 
- AverageTradeReturn, 
"""

class Metric:
    def __init__(self, name: str="metric") -> None:
        self.name = name
        self.reset()

    def update(self, state: State):
        assert isinstance(state, State), f'state must be State, received: {type(state)}'

        return state

    @property
    def result(self):
        raise NotImplementedError
    
    def reset(self, prev_state: State=None):
        assert prev_state is None or isinstance(prev_state, State), f'prev_state must be None or State, received: {type(prev_state)}'

        return prev_state
    

class DifferentActions(Metric):
    def __init__(self, name: str="different_actions") -> None:
        super().__init__(name=name)

    def update(self, state: State):
        super().update(state)

        if not self.prev_state:
            self.prev_state = state
        else:
            if state.allocation_percentage != self.prev_state.allocation_percentage:
                self.different_actions += 1

            self.prev_state = state

    @property
    def result(self):
        return self.different_actions
    
    def reset(self, prev_state: State=None):
        super().reset(prev_state)

        self.prev_state = prev_state
        self.different_actions = 0


class AccountValue(Metric):
    def __init__(self, name: str="account_value") -> None:
        super().__init__(name=name)

    def update(self, state: State):
        super().update(state)

        self.account_value = state.account_value

    @property
    def result(self):
        return self.account_value
    
    def reset(self, prev_state: State=None):
        super().reset(prev_state)
        
        self.account_value = prev_state.account_value if prev_state else 0.0