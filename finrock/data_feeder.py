import pandas as pd

from finrock.state import State

class PdDataFeeder:
    def __init__(
            self, 
            df: pd.DataFrame,
            min: float = None,
            max: float = None
            ) -> None:
        self._df = df
        self._min = min
        self._max = max

        assert isinstance(self._df, pd.DataFrame) == True, "df must be a pandas.DataFrame"
        assert 'timestamp' in self._df.columns, "df must have 'timestamp' column"
        assert 'open' in self._df.columns, "df must have 'open' column"
        assert 'high' in self._df.columns, "df must have 'high' column"
        assert 'low' in self._df.columns, "df must have 'low' column"
        assert 'close' in self._df.columns, "df must have 'close' column"

    @property
    def min(self) -> float:
        return self._min or self._df['low'].min()
    
    @property
    def max(self) -> float:
        return self._max or self._df['high'].max()

    def __len__(self) -> int:
        return len(self._df)
    
    def __getitem__(self, idx: int, args=None) -> State:
        data = self._df.iloc[idx]

        state = State(
            timestamp=data['timestamp'],
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            volume=data.get('volume', 0.0)
        )

        return state
    
    def __iter__(self) -> State:
        """ Create a generator that iterate over the Sequence."""
        for index in range(len(self)):
            yield self[index]