import numpy as np
from .state import Observations

class MinMaxScaler:
    def __init__(self, min: float, max: float):
        self._min = min
        self._max = max
    
    def transform(self, observations: Observations) -> np.ndarray:

        assert isinstance(observations, Observations) == True, "observations must be an instance of Observations"

        transformed_data = []
        for state in observations:
            open = (state.open - self._min) / (self._max - self._min)
            high = (state.high - self._min) / (self._max - self._min)
            low = (state.low - self._min) / (self._max - self._min)
            close = (state.close - self._min) / (self._max - self._min)
            
            transformed_data.append([open, high, low, close, state.allocation_percentage])

        return np.array(transformed_data)
    
    def __call__(self, observations) -> np.ndarray:
        return self.transform(observations)