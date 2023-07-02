from Snakeenv import SnakeEnv


from stable_baselines3 import PPO,DQN

env = SnakeEnv()

env.reset()
env.render_mode = "human"

#models_dir = "models\PPO-1686127347"
#model_path = f"{models_dir}/990000.zip"

#models_dir = "models\PPOV2-1686651773"
#model_path = f"{models_dir}/990000.zip"


models_dir = "models\PPOV3-5M1686657037"
model_path = f"{models_dir}/990000.zip"

"""
models_dir = "models\DQN-1686126776"
model_path = f"{models_dir}/990000.zip"""


model = PPO.load(model_path,env=env)
#model = DQN.load(model_path,env=env)

episodes = 50

results = []

for ep in range(episodes):
    obs, _ = env.reset()
    done = False
    while not done:
        env.render()
        action, _ = model.predict(obs)
        obs,reward,done,trunc,info = env.step(action)

    results.append(env.score)

media = sum(results) / len(results)
print("Media:", media)

# Mínimo y máximo
minimo = min(results)
maximo = max(results)
print("Mínimo:", minimo)
print("Máximo:", maximo)