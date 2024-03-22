from .state import State
import numpy as np

""" Metrics are used to track and log information about the environment.
possible metrics:
+ DifferentActions,
+ AccountValue, 
+ MaxDrawdown, 
+ SharpeRatio, 
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

    @property
    def __name__(self) -> str:
        return self.__class__.__name__

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


class MaxDrawdown(Metric):
    """ The Maximum Drawdown (MDD) is a measure of the largest peak-to-trough decline in the 
    value of a portfolio or investment during a specific period

    The Maximum Drawdown Ratio represents the proportion of the peak value that was lost during 
    the largest decline. It is a measure of the risk associated with a particular investment or 
    portfolio. Investors and fund managers use the Maximum Drawdown and its ratio to assess the 
    historical downside risk and potential losses that could be incurred.
    """
    def __init__(self, name: str="max_drawdown") -> None:
        super().__init__(name=name)

    def update(self, state: State):
        super().update(state)

        # Use min to find the trough value
        self.max_account_value = max(self.max_account_value, state.account_value)

        # Calculate drawdown
        drawdown = (state.account_value - self.max_account_value) / self.max_account_value

        # Update max drawdown if the current drawdown is greater
        self.max_drawdown = min(self.max_drawdown, drawdown)

    @property
    def result(self):
        return self.max_drawdown
    
    def reset(self, prev_state: State=None):
        super().reset(prev_state)

        self.max_account_value = prev_state.account_value if prev_state else 0.0
        self.max_drawdown = 0.0


class SharpeRatio(Metric):
    """ The Sharpe Ratio, is a measure of the risk-adjusted performance of an investment or a portfolio. 
    It helps investors evaluate the return of an investment relative to its risk.

    A higher Sharpe Ratio indicates a better risk-adjusted performance. Investors and portfolio managers 
    often use the Sharpe Ratio to compare the risk-adjusted returns of different investments or portfolios. 
    It allows them to assess whether the additional return earned by taking on additional risk is justified.
    """
    def __init__(self, ratio_days=365.25, name: str='sharpe_ratio'):
        self.ratio_days = ratio_days
        super().__init__(name=name)

    def update(self, state: State):
        super().update(state)
        time_difference_days = (state.date - self.prev_state.date).days
        if time_difference_days >= 1:
            self.daily_returns.append((state.account_value - self.prev_state.account_value) / self.prev_state.account_value)
            self.prev_state = state
        
    @property
    def result(self):
        if len(self.daily_returns) == 0:
            return 0.0

        mean = np.mean(self.daily_returns)
        std = np.std(self.daily_returns)
        if std == 0:
            return 0.0
        
        sharpe_ratio = mean / std * np.sqrt(self.ratio_days)
        
        return sharpe_ratio
    
    def reset(self, prev_state: State=None):
        super().reset(prev_state)
        self.prev_state = prev_state
        self.daily_returns = []