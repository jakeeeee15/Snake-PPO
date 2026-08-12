import torch
import pygame
import time
import sys
import numpy as np
from collections import deque

# Import your custom classes
from playing_model import PpoModel
from game_engine import Engine


def watch_ai_play():
    # 1. Setup the Device and Load the Brain
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading AI on {device}...")

    model = PpoModel().to(device)

    # Change this number to load different generations!
    checkpoint_path = "Version1_best.pth"

    try:
        model.load_state_dict(torch.load(checkpoint_path, map_location=device))
        print(f"Successfully loaded {checkpoint_path}")
    except FileNotFoundError:
        print(f"\nERROR: Could not find {checkpoint_path}.")
        print("Make sure the filename matches what is in your models/ folder!")
        sys.exit()

    # Put the model in evaluation mode (disables random exploration)
    model.eval()

    # 2. Initialize the Game Environment
    # model=False turns Pygame's visual rendering ON
    env = Engine(model=False)
    env.reset()

    # 3. Setup the initial 4-frame visual stack
    frame_stack = deque([env.get_state() for _ in range(4)], maxlen=4)

    print("Starting game! Click the Pygame window to watch.")
    running = True

    while running:
        # Allow the user to close the Pygame window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Stack the 4 frames (3x17x17) into a single (12x17x17) block
        stacked_state = np.concatenate(frame_stack, axis=0)

        # Convert to tensor and add a batch dimension -> [1, 12, 17, 17]
        state_tensor = torch.tensor(stacked_state, dtype=torch.float32).unsqueeze(0).to(device)

        # 4. Ask the AI for its absolute best move
        with torch.no_grad():
            logits, _ = model(state_tensor)

            # argmax picks the #1 most confident move, zero randomness
            action = torch.argmax(logits, dim=-1).item()

        # Step the environment forward based on the AI's decision
        reward, done = env.step(action)

        # Add the new frame to the visual stack
        frame_stack.append(env.get_state())

        # Render the screen
        env.draw()

        # Game Speed: Adjust this to make it play faster or slower
        time.sleep(0.04)

        # 5. Handle Game Over
        if done:
            print(f"Snake Died! Final Score: {env.prev_score}")
            env.reset()
            # Reset the frame stack for the new game
            frame_stack = deque([env.get_state() for _ in range(4)], maxlen=4)

            # Pause for a second before the next round starts
            time.sleep(1)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    watch_ai_play()