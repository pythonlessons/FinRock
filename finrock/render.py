from .state import State

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

class PygameRender:
    def __init__(
            self,
            window_size: int=100,
            screen_width: int=1024,
            screen_height: int=768,
            top_bottom_offset: int=25,
            candle_spacing: int=1,
            color_theme = ColorTheme(),
            frame_rate: int=30,
        ):

        # pygame window settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.top_bottom_offset = top_bottom_offset
        self.candle_spacing = candle_spacing
        self.window_size = window_size
        self.color_theme = color_theme
        self.frame_rate = frame_rate

        self.candle_width = self.screen_width // self.window_size - self.candle_spacing
        self.chart_height = self.screen_height - 2 * self.top_bottom_offset

        self._states = []

        try:
            import pygame
            self.pygame = pygame
        except ImportError:
            raise ImportError('Please install pygame (pip install pygame)')
        
        self.pygame.init()
        self.pygame.display.init()
        self.screen_shape = (self.screen_width, self.screen_height)
        self.window = self.pygame.display.set_mode(self.screen_shape, self.pygame.RESIZABLE)
        self.clock = self.pygame.time.Clock()

    def reset(self):
        self._states = []

    def _map_price_to_window(self, price, max_low, max_high):
        max_range = max_high - max_low
        value = int(self.chart_height - (price - max_low) / max_range * self.chart_height) + self.top_bottom_offset
        return value
    
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
                    self.screen_shape = (event.w, event.h)

            # self.screen.fill(self.color_theme.background)
            canvas = func(self, info)
            canvas = self.pygame.transform.scale(canvas, self.screen_shape)
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            self.pygame.display.update()
            self.clock.tick(self.frame_rate)

            if rgb_array:
                return self.pygame.surfarray.array3d(canvas)

        return wrapper

    @_prerender
    def render(self, info: dict):

        canvas = self.pygame.Surface((self.screen_width , self.screen_height))
        canvas.fill(self.color_theme.background)
        
        max_high = max([state.high for state in self._states])
        max_low = min([state.low for state in self._states])

        candle_offset = self.candle_spacing

        for state in self._states[-self.window_size:]:

            assert isinstance(state, State) == True # check if state is a State object

            # Calculate candle coordinates
            candle_y_open = self._map_price_to_window(state.open, max_low, max_high)
            candle_y_close = self._map_price_to_window(state.close, max_low, max_high)
            candle_y_high = self._map_price_to_window(state.high, max_low, max_high)
            candle_y_low = self._map_price_to_window(state.low, max_low, max_high)

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
            self.pygame.draw.line(canvas, self.color_theme.wick, (candle_offset + self.candle_width // 2, candle_y_high), (candle_offset + self.candle_width // 2, candle_y_low))

            # Draw candlestick body
            self.pygame.draw.rect(canvas, candle_color, (candle_offset, candle_body_y, self.candle_width, candle_body_height))

            # Move to the next candle
            candle_offset += self.candle_width + self.candle_spacing

        return canvas