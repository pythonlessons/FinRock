## [0.5.0] - 2024-01-30
### Added:
- Added `MACD` indicator to `indicators` file.
- Added `reward.AccountValueChangeReward` object to calculate reward based on the change in the account value.
- Added `scalers.ZScoreScaler` that doesn't require min and max to transform data, but uses mean and std instead.
- Added `ActionSpace` object to handle the action space of the agent.
- Added support for continuous actions. (float values between 0 and 1)

### Changed:
- Updated all indicators to have `config` parameter, that we can use so we can serialize the indicators. (save/load configurations to/from file)
- Changed `reward.simpleReward` to `reward.SimpleReward` Object.
- Updated `state.State` to have `open`, `high`, `low`, `close` and `volume` attributes.
- Updated `data_feeder.PdDataFeeder` to be serializable by including `save_config` and `load_config` methods.
- Included trading fees into `trading_env.TradingEnv` object.
- Updated `trading_env.TradingEnv` to have `reset` method, which resets the environment to the initial state.
- Included `save_config` and `load_config` methods into `trading_env.TradingEnv` object, so we can save/load the environment configuration.

## [0.4.0] - 2024-01-02
### Added:
- Created `indicators` file, where I added `BolingerBands`, `RSI`, `PSAR`, `SMA` indicators
- Added `SharpeRatio` and `MaxDrawdown` metrics to `metrics`
- Included indicators handling into `data_feeder.PdDataFeeder` object
- Included indicators handling into `state.State` object

### Changed:
- Changed `finrock` package dependency from `0.0.4` to `0.4.1`
- Refactored `render.PygameRender` object to handle indicators rendering (getting very messy)
- Updated `scalers.MinMaxScaler` to handle indicators scaling
- Updated `trading_env.TradingEnv` to raise an error with `np.nan` data and skip `None` states


## [0.3.0] - 2023-12-05
### Added:
- Added `DifferentActions` and `AccountValue` as metrics. Metrics are the main way to evaluate the performance of the agent.
- Now `metrics.Metrics` object can be used to calculate the metrics within trading environment.
- Included `rockrl==0.0.4` as a dependency, which is a reinforcement learning package that I created.
- Added `experiments/training_ppo_sinusoid.py` to train a simple Dense agent using PPO algorithm on the sinusoid data with discrete actions.
- Added `experiments/testing_ppo_sinusoid.py` to test the trained agent on the sinusoid data with discrete actions.

### Changed:
- Renamed and moved `playing.py` to `experiments/playing_random_sinusoid.py`
- Upgraded `finrock.render.PygameRender`, now we can stop/resume rendering with spacebar and render account value along with the actions


## [0.2.0] - 2023-11-29
### Added:
- Created `reward.simpleReward` function to calculate reward based on the action and the difference between the current price and the previous price
- Created `scalers.MinMaxScaler` object to transform the price data to a range between 0 and 1 and prepare it for the neural networks input
- Created `state.Observations` object to hold the observations of the agent with set window size
- Updated `render.PygameRender` object to render the agent's actions
- Updated `state.State` to hold current state `assets`, `balance` and `allocation_percentage` on specific State


## [0.1.0] - 2023-10-17
### Initial Release:
- Created the project
- Created code to create random sinusoidal price data
- Created `state.State` object, which holds the state of the market
- Created `render.PygameRender` object, which renders the state of the market using `pygame` library
- Created `trading_env.TradingEnv` object, which is the environment for the agent to interact with
- Created `data_feeder.PdDataFeeder` object, which feeds the environment with data from a pandas dataframe