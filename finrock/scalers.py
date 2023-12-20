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
            data = []
            for name in ['open', 'high', 'low', 'close']:
                value = getattr(state, name)
                transformed_value = (value - self._min) / (self._max - self._min)
                data.append(transformed_value)
            
            data.append(state.allocation_percentage)

            # append scaled indicators
            for indicator in state.indicators:
                for value in indicator["values"].values():
                    transformed_value = (value - indicator["min"]) / (indicator["max"] - indicator["min"])
                    data.append(transformed_value)

            transformed_data.append(data)

        return np.array(transformed_data)
    
    def __call__(self, observations) -> np.ndarray:
        return self.transform(observations)