import pandas as pd

from .render import RenderOptions, RenderType, WindowType

""" Implemented indicators:
- SMA
- Bolinger Bands
- RSI
- PSAR
- MACD (Moving Average Convergence Divergence)

TODO:
- Commodity Channel Index (CCI), and X is the 
- Average Directional Index (ADX)
"""

    
class Indicator:
    """ Base class for indicators
    """
    def __init__(
            self, 
            data: pd.DataFrame, 
            target_column: str='close',
            render_options: dict={},
            min: float=None,
            max: float=None,
            **kwargs
        ) -> None:
        self._data = data.copy()
        self._target_column = target_column
        self._custom_render_options = render_options
        self._render_options = render_options
        self._min = min # if min is not None else self._data[target_column].min()
        self._max = max # if max is not None else self._data[target_column].max()
        self.values = {}

        assert isinstance(self._data, pd.DataFrame) == True, "data must be a pandas.DataFrame"
        assert self._target_column in self._data.columns, f"data must have '{self._target_column}' column"

        self.compute()
        if not self._custom_render_options:
            self._render_options = self.default_render_options() 

    @property
    def min(self):
        return self._min
    
    @min.setter
    def min(self, min: float):
        self._min = self._min or min
        if not self._custom_render_options:
            self._render_options = self.default_render_options() 
    
    @property
    def max(self):
        return self._max
    
    @max.setter
    def max(self, max: float):
        self._max = self._max or max
        if not self._custom_render_options:
            self._render_options = self.default_render_options() 

    @property
    def target_column(self):
        return self._target_column

    @property
    def __name__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self):
        return self.__name__

    @property
    def names(self):
        return self._names
    
    def compute(self):
        raise NotImplementedError
    
    def default_render_options(self):
        return {}

    def render_options(self):
        return {name: option.copy() for name, option in self._render_options.items()}

    def __getitem__(self, index: int):
        row = self._data.iloc[index]
        for name in self.names:
            if pd.isna(row[name]):
                return None
            
            self.values[name] = row[name]
            if self._render_options.get(name):
                self._render_options[name].value = row[name]

        return self.serialise()

    def __call__(self, index: int):
        return self[index]
    
    def serialise(self):
        return {
            'name': self.name,
            'names': self.names,
            'values': self.values.copy(),
            'target_column': self.target_column,
            'render_options': self.render_options(),
            'min': self.min,
            'max': self.max
        }
    
    def config(self):
        return {
            'name': self.name,
            'names': self.names,
            'target_column': self.target_column,
            'min': self.min,
            'max': self.max
        }
        


class SMA(Indicator):
    """ Trend indicator

    A simple moving average (SMA) calculates the average of a selected range of prices, usually closing prices, by the number 
    of periods in that range.

    The SMA is a technical indicator for determining if an asset price will continue or reverse a bull or bear trend. It is 
    calculated by summing up the closing prices of a stock over time and then dividing that total by the number of time periods 
    being examined. Short-term averages respond quickly to changes in the price of the underlying, while long-term averages are 
    slow to react.

    https://www.investopedia.com/terms/s/sma.asp
    """
    def __init__(
            self, 
            data: pd.DataFrame, 
            period: int=20, 
            target_column: str='close',
            render_options: dict={},
            **kwargs
        ):
        self._period = period
        self._names = [f'SMA{period}']
        super().__init__(data, target_column, render_options, **kwargs)
        self.min = self._data[self._names[0]].min()
        self.max = self._data[self._names[0]].max()
    
    def default_render_options(self):
        return {name: RenderOptions(
            name=name,
            color=(100, 100, 255),
            window_type=WindowType.MAIN,
            render_type=RenderType.LINE,
            min=self.min,
            max=self.max
        ) for name in self._names}

    def compute(self):
        self._data[self.names[0]] = self._data[self.target_column].rolling(self._period).mean()

    def config(self):
        config = super().config()
        config['period'] = self._period
        return config


class BolingerBands(Indicator):
    """ Volatility indicator

    Bollinger Bands are a type of price envelope developed by John BollingerOpens in a new window. (Price envelopes define 
    upper and lower price range levels.) Bollinger Bands are envelopes plotted at a standard deviation level above and 
    below a simple moving average of the price. Because the distance of the bands is based on standard deviation, they 
    adjust to volatility swings in the underlying price.

    Bollinger Bands use 2 parameters, Period and Standard Deviations, StdDev. The default values are 20 for period, and 2 
    for standard deviations, although you may customize the combinations.

    Bollinger bands help determine whether prices are high or low on a relative basis. They are used in pairs, both upper
    and lower bands and in conjunction with a moving average. Further, the pair of bands is not intended to be used on its own. 
    Use the pair to confirm signals given with other indicators.
    """
    def __init__(
            self, 
            data: pd.DataFrame, 
            period: int=20, 
            std: int=2,
            target_column: str='close',
            render_options: dict={},
            **kwargs
        ):
        self._period = period
        self._std = std
        self._names = ['SMA', 'BB_up', 'BB_dn']
        super().__init__(data, target_column, render_options, **kwargs)
        self.min = self._data['BB_dn'].min()
        self.max = self._data['BB_up'].max()

    def compute(self):
        self._data['SMA'] = self._data[self.target_column].rolling(self._period).mean()
        self._data['BB_up'] = self._data['SMA'] + self._data[self.target_column].rolling(self._period).std() * self._std
        self._data['BB_dn'] = self._data['SMA'] - self._data[self.target_column].rolling(self._period).std() * self._std

    def default_render_options(self):
        return {name: RenderOptions(
            name=name,
            color=(100, 100, 255),
            window_type=WindowType.MAIN,
            render_type=RenderType.LINE,
            min=self.min,
            max=self.max
        ) for name in self._names}

    def config(self):
        config = super().config()
        config['period'] = self._period
        config['std'] = self._std
        return config

class RSI(Indicator):
    """ Momentum indicator

    The Relative Strength Index (RSI), developed by J. Welles Wilder, is a momentum oscillator that measures the speed and 
    change of price movements. The RSI oscillates between zero and 100. Traditionally the RSI is considered overbought when 
    above 70 and oversold when below 30. Signals can be generated by looking for divergences and failure swings. 
    RSI can also be used to identify the general trend.
    """
    def __init__(
            self, 
            data: pd.DataFrame, 
            period: int=14, 
            target_column: str='close',
            render_options: dict={},
            min: float=0.0,
            max: float=100.0,
            **kwargs
        ):
        self._period = period
        self._names = ['RSI']
        super().__init__(data, target_column, render_options, min=min, max=max, **kwargs)

    def compute(self):
        delta = self._data[self.target_column].diff()
        up = delta.clip(lower=0)
        down = -1 * delta.clip(upper=0)
        ema_up = up.ewm(com=self._period-1, adjust=True, min_periods=self._period).mean()
        ema_down = down.ewm(com=self._period-1, adjust=True, min_periods=self._period).mean()
        rs = ema_up / ema_down
        self._data['RSI'] = 100 - (100 / (1 + rs))

    def default_render_options(self):
        custom_options = {
            "RSI0": 0,
            "RSI30": 30,
            "RSI70": 70,
            "RSI100": 100
            }
        options = {name: RenderOptions(
            name=name,
            color=(100, 100, 255),
            window_type=WindowType.SEPERATE,
            render_type=RenderType.LINE,
            min=self.min,
            max=self.max
        ) for name in self._names}

        for name, value in custom_options.items():
            options[name] = RenderOptions(
                name=name,
                color=(192, 192, 192),
                window_type=WindowType.SEPERATE,
                render_type=RenderType.LINE,
                min=self.min,
                max=self.max,
                value=value
            )
        return options

    def config(self):
        config = super().config()
        config['period'] = self._period
        return config


class PSAR(Indicator):
    """ Parabolic Stop and Reverse (Parabolic SAR)

    The Parabolic Stop and Reverse, more commonly known as the
    Parabolic SAR,is a trend-following indicator developed by
    J. Welles Wilder. The Parabolic SAR is displayed as a single
    parabolic line (or dots) underneath the price bars in an uptrend,
    and above the price bars in a downtrend.

    https://school.stockcharts.com/doku.php?id=technical_indicators:parabolic_sar
    """
    def __init__(
            self, 
            data: pd.DataFrame, 
            step: float=0.02, 
            max_step: float=0.2,
            target_column: str='close',
            render_options: dict={},
            **kwargs
        ):
        self._names = ['PSAR']
        self._step = step
        self._max_step = max_step
        super().__init__(data, target_column, render_options, **kwargs)
        self.min = self._data['PSAR'].min()
        self.max = self._data['PSAR'].max()

    def default_render_options(self):
        return {name: RenderOptions(
            name=name,
            color=(100, 100, 255),
            window_type=WindowType.MAIN,
            render_type=RenderType.DOT,
            min=self.min,
            max=self.max
        ) for name in self._names}

    def compute(self):
        high = self._data['high']
        low = self._data['low']
        close = self._data[self.target_column]

        up_trend = True
        acceleration_factor = self._step
        up_trend_high = high.iloc[0]
        down_trend_low = low.iloc[0]

        self._psar = close.copy()
        self._psar_up = pd.Series(index=self._psar.index, dtype="float64")
        self._psar_down = pd.Series(index=self._psar.index, dtype="float64")

        for i in range(2, len(close)):
            reversal = False

            max_high = high.iloc[i]
            min_low = low.iloc[i]

            if up_trend:
                self._psar.iloc[i] = self._psar.iloc[i - 1] + (
                    acceleration_factor * (up_trend_high - self._psar.iloc[i - 1])
                )

                if min_low < self._psar.iloc[i]:
                    reversal = True
                    self._psar.iloc[i] = up_trend_high
                    down_trend_low = min_low
                    acceleration_factor = self._step
                else:
                    if max_high > up_trend_high:
                        up_trend_high = max_high
                        acceleration_factor = min(
                            acceleration_factor + self._step, self._max_step
                        )

                    low1 = low.iloc[i - 1]
                    low2 = low.iloc[i - 2]
                    if low2 < self._psar.iloc[i]:
                        self._psar.iloc[i] = low2
                    elif low1 < self._psar.iloc[i]:
                        self._psar.iloc[i] = low1
            else:
                self._psar.iloc[i] = self._psar.iloc[i - 1] - (
                    acceleration_factor * (self._psar.iloc[i - 1] - down_trend_low)
                )

                if max_high > self._psar.iloc[i]:
                    reversal = True
                    self._psar.iloc[i] = down_trend_low
                    up_trend_high = max_high
                    acceleration_factor = self._step
                else:
                    if min_low < down_trend_low:
                        down_trend_low = min_low
                        acceleration_factor = min(
                            acceleration_factor + self._step, self._max_step
                        )

                    high1 = high.iloc[i - 1]
                    high2 = high.iloc[i - 2]
                    if high2 > self._psar.iloc[i]:
                        self._psar[i] = high2
                    elif high1 > self._psar.iloc[i]:
                        self._psar.iloc[i] = high1

            up_trend = up_trend != reversal  # XOR

            if up_trend:
                self._psar_up.iloc[i] = self._psar.iloc[i]
            else:
                self._psar_down.iloc[i] = self._psar.iloc[i]

        # calculate psar indicator
        self._data['PSAR'] = self._psar

    def config(self):
        config = super().config()
        config['step'] = self._step
        config['max_step'] = self._max_step
        return config
    

class MACD(Indicator):
    """ Moving Average Convergence Divergence (MACD)
    """
    def __init__(
            self, 
            data: pd.DataFrame, 
            fast_ma: int = 12,
            slow_ma: int = 26,
            histogram: int = 9,
            target_column: str='close',
            render_options: dict={}, 
            **kwargs
        ):
        self._fast_ma = fast_ma
        self._slow_ma = slow_ma
        self._histogram = histogram
        self._names = ['MACD', 'MACD_signal']
        super().__init__(data, target_column, render_options, **kwargs)
        self.min = self._data['MACD_signal'].min()
        self.max = self._data['MACD_signal'].max()

    def compute(self):
        # Calculate the Short Term Exponential Moving Average (EMA)
        short_ema = self._data[self.target_column].ewm(span=self._fast_ma, adjust=False).mean()

        # Calculate the Long Term Exponential Moving Average (EMA)
        long_ema = self._data[self.target_column].ewm(span=self._slow_ma, adjust=False).mean()

        # Calculate the Moving Average Convergence/Divergence (MACD)
        self._data["MACD"] = short_ema - long_ema

        # Calculate the Signal Line
        self._data["MACD_signal"] = self._data["MACD"].ewm(span=9, adjust=False).mean()

    def default_render_options(self):
        return {name: RenderOptions(
            name=name,
            color=(100, 100, 255),
            window_type=WindowType.SEPERATE,
            render_type=RenderType.LINE,
            min=self.min,
            max=self.max
        ) for name in self._names}
    
    def config(self):
        config = super().config()
        config['fast_ma'] = self._fast_ma
        config['slow_ma'] = self._slow_ma
        config['histogram'] = self._histogram
        return config