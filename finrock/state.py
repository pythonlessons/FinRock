import typing
from datetime import datetime

class State:
    def __init__(
            self, 
            timestamp: str, 
            open: float, 
            high: float, 
            low: float, 
            close: float, 
            volume: float=0.0
        ):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

        try:
            self.date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            raise ValueError(f'received invalid timestamp date format: {timestamp}, expected: YYYY-MM-DD HH:MM:SS')
        
        self._balance = 0.0 # balance in cash
        self._assets = 0.0 # balance in assets
        self._allocation_percentage = 0.0 # percentage of assets allocated to this state
        
    @property
    def balance(self):
        return self._balance
    
    @balance.setter
    def balance(self, value: float):
        self._balance = value

    @property
    def assets(self):
        return self._assets
    
    @assets.setter
    def assets(self, value: float):
        self._assets = value

    @property
    def account_value(self):
        return self.balance + self.assets * self.close

    @property
    def allocation_percentage(self):
        return self._allocation_percentage
    
    @allocation_percentage.setter
    def allocation_percentage(self, value: float):
        assert 0.0 <= value <= 1.0, f'allocation_percentage value must be between 0.0 and 1.0, received: {value}'
        self._allocation_percentage = value
    

class Observations:
    def __init__(
            self, 
            window_size: int,
            observations: typing.List[State]=[],
        ):
        self._observations = observations
        self._window_size = window_size

        assert isinstance(self._observations, list) == True, "observations must be a list"
        assert len(self._observations) <= self._window_size, f'observations length must be <= window_size, received: {len(self._observations)}'
        assert all(isinstance(observation, State) for observation in self._observations) == True, "observations must be a list of State objects"

    def __len__(self) -> int:
        return len(self._observations)
    
    @property
    def window_size(self) -> int:
        return self._window_size
    
    @property
    def observations(self) -> typing.List[State]:
        return self._observations
    
    @property
    def full(self) -> bool:
        return len(self._observations) == self._window_size
    
    def __getitem__(self, idx: int) -> State:
        try:
            return self._observations[idx]
        except IndexError:
            raise IndexError(f'index out of range: {idx}, observations length: {len(self._observations)}')
        
    def __iter__(self) -> State:
        """ Create a generator that iterate over the Sequence."""
        for index in range(len(self)):
            yield self[index]

    def reset(self) -> None:
        self._observations = []
    
    def append(self, state: State) -> None:
        assert isinstance(state, State) == True, "state must be a State object"
        self._observations.append(state)

        if len(self._observations) > self._window_size:
            self._observations.pop(0)