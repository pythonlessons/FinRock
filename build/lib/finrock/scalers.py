import numpy as np
np.seterr(all="ignore")
import warnings
from .state import Observations


class Scaler:
    def __init__(self):
        pass
    
    def transform(self, observations: Observations) -> np.ndarray:
        raise NotImplementedError
    
    def __call__(self, observations) -> np.ndarray:
        assert isinstance(observations, Observations) == True, "observations must be an instance of Observations"
        return self.transform(observations)
    
    @property
    def __name__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        return self.__name__


class MinMaxScaler(Scaler):
    def __init__(self, min: float, max: float):
        super().__init__()
        self._min = min
        self._max = max
    
    def transform(self, observations: Observations) -> np.ndarray:
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

        results = np.array(transformed_data)

        return results
    

class ZScoreScaler(Scaler):
    def __init__(self):
        super().__init__()
        warnings.filterwarnings("ignore", category=RuntimeWarning, message="overflow encountered in reduce")
    
    def transform(self, observations: Observations) -> np.ndarray:
        full_data = []
        for state in observations:
            data = [getattr(state, name) for name in ['open', 'high', 'low', 'close', 'allocation_percentage']]
            data += [value for indicator in state.indicators for value in indicator["values"].values()]
            full_data.append(data)

        results = np.array(full_data)

        # nan to zero, when divided by zero and allocation_percentage is not changed
        returns = np.nan_to_num(np.diff(results, axis=0) / results[:-1])

        z_scores = np.nan_to_num((returns - np.mean(returns, axis=0)) / np.std(returns, axis=0))

        return z_scores