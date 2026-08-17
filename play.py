import torch
import pygame
import time
import sys
import numpy as np
from collections import deque
from torch.distributions import Categorical

# Import your custom classes
from playing_model import PpoModel
from game_engine import Engine


# EXACT FrameStack from your training environment
class FrameStack:
    def __init__(self):
        queue = np.zeros((3, 17, 17))
        self.stack = deque(maxlen=4)
        for _ in range(4):
            self.stack.append(queue)

    def add(self, new_frames):
        self.stack.append(new_frames)


def watch_ai_play():
    # 1. Setup the Device and Load the Brain
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading AI on {device}...")

    model = PpoModel().to(device)

    # Change this number to load your target generation!
    checkpoint_path = "models/snake_ppo_gen_70800.pth"

    try:
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        print(f"Successfully loaded {checkpoint_path}")
    except FileNotFoundError:
        print(f"\nERROR: Could not find {checkpoint_path}.")
        print("Make sure the filename matches what is in your models/ folder!")
        sys.exit()

    # Put the model in evaluation mode
    model.eval()

    # 2. Initialize the Game Environment
    env = Engine(model=False)
    env.reset()

    # 3. Setup the 4-frame visual stack EXACTLY like your Vector_Engine training
    frame_stack = FrameStack()

    # Push 4 identical copies of the starting frame to establish zero velocity
    initial_state = env.get_state()
    for _ in range(4):
        frame_stack.add(initial_state)

    print("Starting game! Click the Pygame window to watch.")
    running = True
    i = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 4. Format the state EXACTLY how vector_engine formats it
        # This converts the deque to (1, 4, 3, 17, 17) and reshapes to (1, 12, 17, 17)
        stacks = [frame_stack.stack]
        stack_array = np.array(stacks, dtype=np.float32).reshape((1, 12, 17, 17))

        # Push to GPU
        state_tensor = torch.tensor(stack_array).to(device)

        # 5. Ask the AI for its move
        with torch.no_grad():
            logits, _ = model(state_tensor)

            # argmax picks the absolute highest confidence move.
            # If it still acts stubborn at Gen 4200, swap this out for Categorical sample()
            action = torch.argmax(logits, dim=-1).item()

            # dist = Categorical(logits=logits)
            # action = dist.sample().item()

        # Step the environment forward using the 3-action AI engine block
        reward, done = env.model_step(action)

        # Add the new frame to the visual stack
        frame_stack.add(env.get_state())

        # Render the screen
        env.draw()

        # Game Speed: Adjust this to make it play faster or slower
        time.sleep(0.04)

        # 6. Handle Game Over
        if done:
            print(f"Snake Died! Final Score: {env.prev_score}")
            env.reset()

            # Reset the frame stack properly for the next game!
            frame_stack = FrameStack()
            reset_state = env.get_state()
            for _ in range(4):
                frame_stack.add(reset_state)

            i += 1
            time.sleep(1)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    watch_ai_play()