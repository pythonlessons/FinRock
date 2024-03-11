from enum import Enum
from .state import State

class RenderType(Enum):
    LINE = 0
    DOT = 1

class WindowType(Enum):
    MAIN = 0
    SEPERATE = 1

class RenderOptions:
    def __init__(
            self, 
            name: str,
            color: tuple,
            window_type: WindowType,
            render_type: RenderType, 
            min: float, 
            max: float, 
            value: float = None,
        ):
        self.name = name
        self.color = color
        self.window_type = window_type
        self.render_type = render_type
        self.min = min
        self.max = max
        self.value = value

    def copy(self):
        return RenderOptions(
            name=self.name,
            color=self.color,
            window_type=self.window_type,
            render_type=self.render_type,
            min=self.min,
            max=self.max,
            value=self.value
        )

class ColorTheme:
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 10, 0)
    lightblue = (100, 100, 255)
    green = (0, 240, 0)

    background = black
    up_candle = green
    down_candle = red
    wick = white
    text = white
    buy = green
    sell = red
    font = 'Noto Sans'
    font_ratio = 0.02

class MainWindow:
    def __init__(
            self, 
            width: int, 
            height: int, 
            top_offset: int,
            bottom_offset: int,
            window_size: int,
            candle_spacing,
            font_ratio: float=0.02,
            spacing_ratio: float=0.02,
            split_offset: int=0
        ):
        self.width = width
        self.height = height
        self.top_offset = top_offset
        self.bottom_offset = bottom_offset
        self.window_size = window_size
        self.candle_spacing = candle_spacing
        self.font_ratio = font_ratio
        self.spacing_ratio = spacing_ratio
        self.split_offset = split_offset

        self.seperate_window_ratio = 0.15

    @property
    def font_size(self):
        return int(self.height * self.font_ratio)

    @property
    def candle_width(self):
        return self.width // self.window_size - self.candle_spacing
    
    @property
    def chart_height(self):
        return self.height - (2 * self.top_offset + self.bottom_offset)
    
    @property
    def spacing(self):
        return int(self.height * self.spacing_ratio)
    
    @property
    def screen_shape(self):
        return (self.width, self.height)
    
    @screen_shape.setter
    def screen_shape(self, value: tuple):
        self.width, self.height = value

    def map_price_to_window(self, price: float, max_low: float, max_high: float):
        max_range = max_high - max_low
        height = self.chart_height - self.split_offset - self.bottom_offset - self.top_offset * 2
        value = int(height - (price - max_low) / max_range * height) + self.top_offset
        return value
    
    def map_to_seperate_window(self, value: float, min: float, max: float):
        self.split_offset = int(self.height * self.seperate_window_ratio)
        max_range = max - min
        new_value = int(self.split_offset - (value - min) / max_range * self.split_offset)
        height = self.chart_height - self.split_offset + new_value
        return height


class PygameRender:
    def __init__(
            self,
            window_size: int=100,
            screen_width: int=1440,
            screen_height: int=1080,
            top_offset: int=25,
            bottom_offset: int=25,
            candle_spacing: int=1,
            color_theme = ColorTheme(),
            frame_rate: int=30,
            render_balance: bool=True,
        ):
        # pygame window settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.top_offset = top_offset
        self.bottom_offset = bottom_offset
        self.candle_spacing = candle_spacing
        self.window_size = window_size
        self.color_theme = color_theme
        self.frame_rate = frame_rate
        self.render_balance = render_balance

        self.mainWindow = MainWindow(
            width=self.screen_width,
            height=self.screen_height,
            top_offset=self.top_offset,
            bottom_offset=self.bottom_offset,
            window_size=self.window_size,
            candle_spacing=self.candle_spacing,
            font_ratio=self.color_theme.font_ratio
        )

        self._states = []

        try:
            import pygame
            self.pygame = pygame
        except ImportError:
            raise ImportError('Please install pygame (pip install pygame)')
        
        self.pygame.init()
        self.pygame.display.init()
        self.window = self.pygame.display.set_mode(self.mainWindow.screen_shape, self.pygame.RESIZABLE)
        self.clock = self.pygame.time.Clock()

    def reset(self):
        self._states = []
    
    def _prerender(func):
        """ Decorator for input data validation and pygame window rendering"""
        def wrapper(self, info: dict, rgb_array: bool=False):
            self._states += info.get('states', [])

            if not self._states or not bool(self.window._pixels_address):
                return

            for event in self.pygame.event.get():
                if event.type == self.pygame.QUIT:
                    self.pygame.quit()
                    return

                if event.type == self.pygame.VIDEORESIZE:
                    self.mainWindow.screen_shape = (event.w, event.h)

                # pause if spacebar is pressed
                if event.type == self.pygame.KEYDOWN:
                    if event.key == self.pygame.K_SPACE:
                        print('Paused')
                        while True:
                            event = self.pygame.event.wait()
                            if event.type == self.pygame.KEYDOWN:
                                if event.key == self.pygame.K_SPACE:
                                    print('Unpaused')
                                    break
                            if event.type == self.pygame.QUIT:
                                self.pygame.quit()
                                return
                            
                        self.mainWindow.screen_shape = self.pygame.display.get_surface().get_size()


            canvas = func(self, info)
            canvas = self.pygame.transform.scale(canvas, self.mainWindow.screen_shape)
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            self.pygame.display.update()
            self.clock.tick(self.frame_rate)

            if rgb_array:
                return self.pygame.surfarray.array3d(canvas)

        return wrapper
    
    def render_indicators(self, state: State, canvas: object, candle_offset: int, max_low: float, max_high: float):
        # connect last 2 points with a line
        for i, indicator in enumerate(state.indicators):
            for name, render_option in indicator["render_options"].items():

                index = self._states.index(state)
                if not index:
                    return
                last_state = self._states[index - 1]

                if render_option.render_type == RenderType.LINE:
                    prev_render_option = last_state.indicators[i]["render_options"][name]
                    if render_option.window_type == WindowType.MAIN:

                        cur_value_map = self.mainWindow.map_price_to_window(render_option.value, max_low, max_high)
                        prev_value_map = self.mainWindow.map_price_to_window(prev_render_option.value, max_low, max_high)

                    elif render_option.window_type == WindowType.SEPERATE:

                        cur_value_map = self.mainWindow.map_to_seperate_window(render_option.value, render_option.min, render_option.max)
                        prev_value_map = self.mainWindow.map_to_seperate_window(prev_render_option.value, prev_render_option.min, prev_render_option.max)

                    self.pygame.draw.line(canvas, render_option.color, 
                                            (candle_offset - self.mainWindow.candle_width / 2, prev_value_map), 
                                            (candle_offset + self.mainWindow.candle_width / 2, cur_value_map))
                    
                elif render_option.render_type == RenderType.DOT:
                    if render_option.window_type == WindowType.MAIN:
                        self.pygame.draw.circle(canvas, render_option.color,
                                                (candle_offset, self.mainWindow.map_price_to_window(render_option.value, max_low, max_high)), 2)
                    elif render_option.window == WindowType.SEPERATE:
                        raise NotImplementedError('Seperate window for indicators is not implemented yet')
                
    def render_candle(self, state: State, canvas: object, candle_offset: int, max_low: float, max_high: float, font: object):
        assert isinstance(state, State) == True # check if state is a State object

        # Calculate candle coordinates
        candle_y_open = self.mainWindow.map_price_to_window(state.open, max_low, max_high)
        candle_y_close = self.mainWindow.map_price_to_window(state.close, max_low, max_high)
        candle_y_high = self.mainWindow.map_price_to_window(state.high, max_low, max_high)
        candle_y_low = self.mainWindow.map_price_to_window(state.low, max_low, max_high)

        # Determine candle color
        if state.open < state.close:
            # up candle
            candle_color = self.color_theme.up_candle
            candle_body_y = candle_y_close
            candle_body_height = candle_y_open - candle_y_close
        else:
            # down candle
            candle_color = self.color_theme.down_candle
            candle_body_y = candle_y_open
            candle_body_height = candle_y_close - candle_y_open

        # Draw candlestick wicks
        self.pygame.draw.line(canvas, self.color_theme.wick, 
                              (candle_offset + self.mainWindow.candle_width // 2, candle_y_high), 
                              (candle_offset + self.mainWindow.candle_width // 2, candle_y_low))

        # Draw candlestick body
        self.pygame.draw.rect(canvas, candle_color, (candle_offset, candle_body_y, self.mainWindow.candle_width, candle_body_height))

        # Compare with previous state to determine whether buy or sell action was taken and draw arrow
        index = self._states.index(state)
        if index > 0:
            last_state = self._states[index - 1]

            if last_state.allocation_percentage < state.allocation_percentage:
                # buy
                candle_y_low = self.mainWindow.map_price_to_window(last_state.low, max_low, max_high)
                self.pygame.draw.polygon(canvas, self.color_theme.buy, [
                    (candle_offset - self.mainWindow.candle_width / 2, candle_y_low + self.mainWindow.spacing / 2), 
                    (candle_offset - self.mainWindow.candle_width * 0.1, candle_y_low + self.mainWindow.spacing), 
                    (candle_offset - self.mainWindow.candle_width * 0.9, candle_y_low + self.mainWindow.spacing)
                    ])
                
                # add account_value label bellow candle
                if self.render_balance:
                    text = str(int(last_state.account_value))
                    buy_label = font.render(text, True, self.color_theme.text)
                    label_width, label_height = font.size(text)
                    canvas.blit(buy_label, (candle_offset - (self.mainWindow.candle_width + label_width) / 2, candle_y_low + self.mainWindow.spacing))

            elif last_state.allocation_percentage > state.allocation_percentage:
                # sell
                candle_y_high = self.mainWindow.map_price_to_window(last_state.high, max_low, max_high)
                self.pygame.draw.polygon(canvas, self.color_theme.sell, [
                    (candle_offset - self.mainWindow.candle_width / 2, candle_y_high - self.mainWindow.spacing / 2), 
                    (candle_offset - self.mainWindow.candle_width * 0.1, candle_y_high - self.mainWindow.spacing), 
                    (candle_offset - self.mainWindow.candle_width * 0.9, candle_y_high - self.mainWindow.spacing)
                    ])

                # add account_value label above candle
                if self.render_balance:
                    text = str(int(last_state.account_value))
                    sell_label = font.render(text, True, self.color_theme.text)
                    label_width, label_height = font.size(text)
                    canvas.blit(sell_label, (candle_offset - (self.mainWindow.candle_width + label_width) / 2, candle_y_high - self.mainWindow.spacing - label_height))

    @_prerender
    def render(self, info: dict):
        canvas = self.pygame.Surface(self.mainWindow.screen_shape)
        canvas.fill(self.color_theme.background)
        
        max_high = max([state.high for state in self._states[-self.window_size:]])
        max_low = min([state.low for state in self._states[-self.window_size:]])

        candle_offset = self.candle_spacing

        # Set font for labels
        font = self.pygame.font.SysFont(self.color_theme.font, self.mainWindow.font_size)

        for state in self._states[-self.window_size:]:

            # draw indicators
            self.render_indicators(state, canvas, candle_offset, max_low, max_high)

            # draw candle
            self.render_candle(state, canvas, candle_offset, max_low, max_high, font)

            # Move to the next candle
            candle_offset += self.mainWindow.candle_width + self.candle_spacing

        # Draw max and min ohlc values on the chart
        label_width, label_height = font.size(str(max_low))
        label_y_low = font.render(str(max_low), True, self.color_theme.text)
        canvas.blit(label_y_low, (self.candle_spacing + 5, self.mainWindow.height - label_height * 2))

        label_width, label_height = font.size(str(max_low))
        label_y_high = font.render(str(max_high), True, self.color_theme.text)
        canvas.blit(label_y_high, (self.candle_spacing + 5, label_height))

        return canvas