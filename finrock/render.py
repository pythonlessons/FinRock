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
    buy = green
    sell = red
    font = 'Noto Sans'
    font_size = 15*2

class PygameRender:
    def __init__(
            self,
            window_size: int=100,
            screen_width: int=1024*2,
            screen_height: int=768*2,
            top_bottom_offset: int=25,
            candle_spacing: int=1,
            color_theme = ColorTheme(),
            frame_rate: int=30,
            render_balance: bool=True,
        ):

        # pygame window settings
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.top_bottom_offset = top_bottom_offset
        self.candle_spacing = candle_spacing
        self.window_size = window_size
        self.color_theme = color_theme
        self.frame_rate = frame_rate
        self.render_balance = render_balance

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

        # Set font for labels
        font = self.pygame.font.SysFont(self.color_theme.font, self.color_theme.font_size)

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

            # Compare with previous state to determine whether buy or sell action was taken and draw arrow
            index = self._states.index(state)
            if index > 0:
                last_state = self._states[index - 1]

                if last_state.allocation_percentage < state.allocation_percentage:
                    # buy
                    candle_y_low = self._map_price_to_window(last_state.low, max_low, max_high)
                    self.pygame.draw.polygon(canvas, self.color_theme.buy, [
                        (candle_offset - self.candle_width / 2, candle_y_low + 10), 
                        (candle_offset - self.candle_width / 2 - 5, candle_y_low + 20), 
                        (candle_offset - self.candle_width / 2 + 5, candle_y_low + 20)
                        ])
                    
                    # add account_value label bellow candle
                    if self.render_balance:
                        text = str(int(last_state.account_value))
                        buy_label = font.render(text, True, self.color_theme.text)
                        label_width, label_height = font.size(text)
                        canvas.blit(buy_label, (candle_offset - (self.candle_width + label_width) / 2, candle_y_low + 25))

                elif last_state.allocation_percentage > state.allocation_percentage:
                    # sell
                    candle_y_high = self._map_price_to_window(last_state.high, max_low, max_high)
                    self.pygame.draw.polygon(canvas, self.color_theme.sell, [
                        (candle_offset - self.candle_width / 2, candle_y_high - 10), 
                        (candle_offset - self.candle_width / 2 - 5, candle_y_high - 20), 
                        (candle_offset - self.candle_width / 2 + 5, candle_y_high - 20)
                        ])

                    # add account_value label above candle
                    if self.render_balance:
                        text = str(int(last_state.account_value))
                        sell_label = font.render(text, True, self.color_theme.text)
                        label_width, label_height = font.size(text)
                        canvas.blit(sell_label, (candle_offset - (self.candle_width + label_width) / 2, candle_y_high - 35))

            # Move to the next candle
            candle_offset += self.candle_width + self.candle_spacing

        # Draw max and min ohlc values on the chart
        label_width, label_height = font.size(str(max_low))
        label_y_low = font.render(str(max_low), True, self.color_theme.text)
        canvas.blit(label_y_low, (self.candle_spacing + 5, self.screen_height - label_height * 2))

        label_width, label_height = font.size(str(max_low))
        label_y_high = font.render(str(max_high), True, self.color_theme.text)
        canvas.blit(label_y_high, (self.candle_spacing + 5, label_height))

        return canvas