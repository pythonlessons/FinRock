# FinRock
Reinforcement Learning package for Finance

# Environment Structure:
<p align="center">
  <img src="Tutorials\Documents\04_FinRock.jpg">
</p>

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
  <img src="Tutorials\Documents\04_FinRock_render.png">
</p>

## Links to YouTube videos:
- [Introduction to FinRock package](https://youtu.be/xU_YJB7vilA)
- [Complete Trading Simulation Backbone](https://youtu.be/1z5geob8Yho)
- [Training RL agent on Sinusoid data](https://youtu.be/JkA4BuYvWyE)
- [Training RL agent on Sinusoid data and indiciators](https://youtu.be/bGpBEnKzIdo)

# TODO:
- [ ] Train model on `continuous` actions (control allocation percentage)
- [ ] Add more indicators
- [ ] Add more metrics
- [ ] Add more reward functions
- [ ] Add more scalers
- [ ] Train RL agent on real data
- [ ] Add more RL algorithms
- [ ] Refactor rendering, maybe move to browser?