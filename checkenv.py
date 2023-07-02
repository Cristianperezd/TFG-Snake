from stable_baselines3.common.env_checker import check_env
from Snakeenv import *
from stable_baselines3 import PPO,DQN
import os
import time

env = SnakeEnv()

#check_env(env)



models_dir = f"models/PPOV3-5M{int(time.time())}"
logdir = f"logs/PPOV3-5M{int(time.time())}"

if not os.path.exists(models_dir):
    os.makedirs(models_dir)
if not os.path.exists(models_dir):
    os.makedirs(logdir)

env = SnakeEnv()
env.reset()
#env.render_mode = 'human'

model_name = 'PPO'
if model_name == 'PPO' :
    model = PPO('MlpPolicy',env,verbose=1,tensorboard_log=logdir)
elif model_name == 'DQN':
    model = DQN("MlpPolicy",env,verbose=1,tensorboard_log=logdir,exploration_initial_eps=1.0,exploration_final_eps = 0.1 )
TIMESTEPS = 10000
iters = 0

for i in range(1,500):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{TIMESTEPS*i}")




env.close()