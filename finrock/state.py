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