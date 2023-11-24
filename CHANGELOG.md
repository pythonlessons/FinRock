## [0.2.0] - 2023-11-..
### Added:
- Created `reward.simpleReward` function to calculate reward based on the action and the difference between the current price and the previous price
- Created `scalers.MinMaxScaler` object to transform the price data to a range between 0 and 1 and prepare it for the neural networks input
- Created `state.Observations` object to hold the observations of the agent with set window size
- Updated `render.PygameRender` object to render the agent's actions
- Updated `state.State` to hold current state `assets`, `balance` and `allocation_percentage` on specific State


## [0.1.0] - 2023-10-17
### Initial Release:
- created the project
- created code to create random sinusoidal price data
- created `state.State` object, which holds the state of the market
- created `render.PygameRender` object, which renders the state of the market using `pygame` library
- created `trading_env.TradingEnv` object, which is the environment for the agent to interact with
- created `data_feeder.PdDataFeeder` object, which feeds the environment with data from a pandas dataframe