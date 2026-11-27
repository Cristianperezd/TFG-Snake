"""Train a PPO agent on SnakeEnv. Checkpoints are saved every 10,000 steps."""
import os
import time

from stable_baselines3 import PPO

from snake_env import SnakeEnv

TIMESTEPS = 10000

run_name = f"PPOV3-5M{int(time.time())}"
models_dir = f"models/{run_name}"
logdir = f"logs/{run_name}"
os.makedirs(models_dir, exist_ok=True)
os.makedirs(logdir, exist_ok=True)

env = SnakeEnv()
env.reset()

model = PPO('MlpPolicy', env, verbose=1, tensorboard_log=logdir)

for i in range(1, 500):
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{TIMESTEPS * i}")

env.close()
