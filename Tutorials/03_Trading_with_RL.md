# Complete Trading Simulation Backbone

### Environment Structure:
<p align="center">
  <img src="Documents\03_FinRock.jpg">
</p>

### Link to YouTube video:
https://youtu.be/...

### Link to tutorial code:
https://github.com/pythonlessons/FinRock/tree/0.3.0

### Download tutorial code:
https://github.com/pythonlessons/FinRock/archive/refs/tags/0.3.0.zip


### Install requirements:
```
pip install -r requirements.txt
pip install pygame
pip install .
```

### Create sinusoid data:
```
python bin/create_sinusoid_data.py
```

### Train RL (PPO) agent on discrete actions:
```
experiments/training_ppo_sinusoid.py
```

### Test trained agent (Change path to the saved model):
```
experiments/testing_ppo_sinusoid.py
```

### Environment Render:
<p align="center">
  <img src="Documents\03_FinRock_render.png">
</p>