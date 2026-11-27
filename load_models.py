"""Load a trained PPO checkpoint and play 50 episodes, printing score statistics."""
from stable_baselines3 import PPO

from snake_env import SnakeEnv

# Path to a checkpoint saved by checkenv.py
MODEL_PATH = "models/PPOV3-5M1686657037/990000.zip"
EPISODES = 50

env = SnakeEnv()
env.reset()
env.render_mode = "human"

model = PPO.load(MODEL_PATH, env=env)

results = []
for _ in range(EPISODES):
    obs, _ = env.reset()
    done = False
    while not done:
        env.render()
        action, _ = model.predict(obs)
        obs, reward, done, trunc, info = env.step(action)
    results.append(env.score)

print("Mean:", sum(results) / len(results))
print("Min:", min(results))
print("Max:", max(results))
