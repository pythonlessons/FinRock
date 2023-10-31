import pandas as pd

from finrock.state import State

class PdDataFeeder:
    def __init__(self, df: pd.DataFrame):
        self._df = df

        assert isinstance(self._df, pd.DataFrame) == True
        assert 'timestamp' in self._df.columns
        assert 'open' in self._df.columns
        assert 'high' in self._df.columns
        assert 'low' in self._df.columns
        assert 'close' in self._df.columns

    def __len__(self) -> int:
        return len(self._df)
    
    def __getitem__(self, idx: int) -> State:
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