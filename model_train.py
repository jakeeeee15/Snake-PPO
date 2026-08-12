from playing_model import PpoModel, FrameStack
from vector_engine import Vector_Engine
from torch import nn
from collections import deque
import torch
import numpy as np
import warnings
import time
warnings.filterwarnings('ignore', category=DeprecationWarning)


# 0=nothing, 1=left, 2=right, 3=up, 4=down


def make_memory_buffer(engine: Vector_Engine, model: PpoModel, device, active_scores, num_steps=128):
    running = True
    memory = []
    completed_scores = []

    for step in range(num_steps):
        stacks = engine.get_stacks()
        frame_stack_tensor = torch.tensor(stacks, dtype=torch.float32).to(device)

        with torch.no_grad():
            actions, values, log_probs, _ = model.get_action(frame_stack_tensor)
        actions_list = actions.cpu().tolist()
        rewards, dones = engine.step(actions_list)

        active_scores += np.array(rewards)
        for i in range(len(dones)):
            if dones[i]:
                completed_scores.append(active_scores[i])
                active_scores[i] = 0

        memory.append({
            'states': frame_stack_tensor,
            'values': values,
            'rewards': torch.tensor(rewards, dtype=torch.float32).to(device),
            'log_probs': log_probs,
            'dones': torch.tensor(dones, dtype=torch.float32).to(device),
            'actions': actions
        })
        engine.push_states()
    return memory, active_scores, completed_scores

def update_ppo(model : PpoModel, memory:list[dict], device, optim, GAMMA=0.99, epochs=4, epsilon=0.2):
    returns = []
    disc_rewards = torch.zeros(32).to(device)
    for step in reversed(memory):
        mask = 1.0 - step['dones']
        mask = mask.to(device)
        disc_rewards = step['rewards'] + (GAMMA * disc_rewards * mask)
        returns.insert(0, disc_rewards)

    returns = torch.cat(returns).to(device)
    returns = (returns - returns.mean()) / (returns.std() + 1e-7)


    old_states = torch.cat([m['states'] for m in memory]).to(device)
    old_actions = torch.cat([m['actions'] for m in memory]).to(device)
    old_logprobs = torch.cat([m['log_probs'] for m in memory]).to(device).detach()
    old_values = torch.cat([m['values'] for m in memory]).to(device).detach()

    advantages = returns - old_values.squeeze()
    batch_size = len(advantages)
    mini_batch=128
    for _ in range(epochs):
        random_indices = torch.randperm(batch_size).to(device)

        for i in range(0, batch_size, mini_batch):
            mini_batch_indexes = random_indices[i : i+mini_batch]
            states_batch = old_states[mini_batch_indexes]
            actions_batch = old_actions[mini_batch_indexes]
            logprobs_batch = old_logprobs[mini_batch_indexes]
            returns_batch = returns[mini_batch_indexes]
            advantages_batch = advantages[mini_batch_indexes]

            logits, values = model(states_batch)
            dis = torch.distributions.Categorical(logits=logits)
            new_probs_batch = dis.log_prob(actions_batch)
            entropy = dis.entropy()

            prob_ratio = torch.exp(new_probs_batch - logprobs_batch)
            unclipped_loss_cpi = prob_ratio * advantages_batch
            clipped = torch.clip(prob_ratio, 1-epsilon, 1+epsilon) * advantages_batch

            loss_actor = -torch.min(unclipped_loss_cpi, clipped).mean()
            loss_critic = nn.MSELoss()(values.squeeze(), returns_batch)

            loss = loss_actor + 0.5*loss_critic - 0.02*entropy.mean()

            optim.zero_grad()
            loss.backward()
            optim.step()









if __name__ == '__main__':
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("Device = " + device)
    GENERATIONS = 150000
    NUM_ENV=32
    vec_eng = Vector_Engine(NUM_ENV)
    model = PpoModel().to(device)
    # checkpoint = "models/snake_ppo_gen_12900.pth"
    # model.load_state_dict(torch.load(checkpoint, map_location=device))
    # print(f"Successfully loaded {checkpoint}! Resuming training...")
    vec_eng.reset()
    opt = torch.optim.Adam(params=model.parameters(), lr=0.0003)
    active_scores = np.zeros(NUM_ENV)
    for gen in range(GENERATIONS):
        start_time = time.time()

        memory, active_scores, completed_scores = make_memory_buffer(vec_eng, model, device, active_scores)
        update_ppo(model, memory, device, opt)

        end_time = time.time()

        if len(completed_scores) > 0:
            avg_score = np.mean(completed_scores)
            max_score = np.max(completed_scores)
            print(
                f"Gen {gen:04d} | Time: {end_time - start_time:.1f}s | Avg Reward: {avg_score:>6.2f} | Max Reward: {max_score:>6.2f}")
        else:
            print(f"Gen {gen:04d} | Time: {end_time - start_time:.1f}s | No snakes died this generation.")

        if gen % 300 == 0 and gen > 0:
            torch.save(model.state_dict(), f"models/snake_ppo_gen_{gen}.pth")
            print(f">>> Checkpoint Saved: snake_ppo_gen_{gen}.pth")








