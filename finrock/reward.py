from .state import Observations


def simpleReward(observations: Observations) -> float:
    
    assert isinstance(observations, Observations) == True, "observations must be an instance of Observations"

    last_state, next_state = observations[-2:]

    # buy
    if next_state.allocation_percentage > last_state.allocation_percentage:
        # check whether it was good or bad to buy
        order_size = next_state.allocation_percentage - last_state.allocation_percentage
        reward = (next_state.close - last_state.close) / last_state.close * order_size

    # sell
    elif next_state.allocation_percentage < last_state.allocation_percentage:
        # check whether it was good or bad to sell
        order_size = last_state.allocation_percentage - next_state.allocation_percentage
        reward = -1 * (next_state.close - last_state.close) / last_state.close * order_size

    # hold
    else:
        # check whether it was good or bad to hold
        ratio = -1 if not last_state.allocation_percentage else last_state.allocation_percentage
        reward = (next_state.close - last_state.close) / last_state.close * ratio
        
    return reward