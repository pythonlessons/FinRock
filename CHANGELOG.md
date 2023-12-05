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