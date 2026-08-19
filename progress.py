import os
import re
import time
import torch
import pygame
import numpy as np
from collections import deque
from game_engine import Engine

# Imported exactly from your playing_model based on your traceback
from playing_model import PpoModel

# Setup device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Scan and sort the models directory
model_dir = "models"
if not os.path.exists(model_dir):
    print(f"Error: Could not find the '{model_dir}' directory.")
    exit()

model_files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]


def get_gen_number(filename):
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0


model_files.sort(key=get_gen_number)

if not model_files:
    print("No .pth files found in the 'models' directory.")
    exit()

# Initialize Model and Engine
model = PpoModel().to(device)
model.eval()
gamer = Engine(model=False)

pygame.font.init()
font = pygame.font.SysFont("Arial", 36, bold=True)
small_font = pygame.font.SysFont("Arial", 24, bold=True)

fps = 40

print("\nStarting Showcase...")

for model_file in model_files:
    gen_number = get_gen_number(model_file)
    checkpoint_path = os.path.join(model_dir, model_file)

    print(f"Loading Generation {gen_number}...")

    # Silenced the PyTorch security warning using weights_only=True
    model.load_state_dict(torch.load(checkpoint_path, map_location=device, weights_only=True))

    gamer.reset()
    done = False

    # --- THE 12-CHANNEL FIX ---
    # We must seed the initial stack with 4 identical copies of the starting frame
    state = gamer.get_state()
    state_stack = deque([state] * 4, maxlen=4)

    time.sleep(1)

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        # 1. Stack the 4 frames into a single 12-channel numpy array
        stacked_state = np.concatenate(state_stack, axis=0)

        # 2. Convert to tensor (1, 12, 17, 17)
        state_tensor = torch.tensor(stacked_state, dtype=torch.float32).unsqueeze(0).to(device)

        # 3. Ask the AI for its move
        with torch.no_grad():
            logits, _ = model(state_tensor)
            action = torch.argmax(logits, dim=-1).item()

        # 4. Execute the move
        reward, done = gamer.model_step(action)

        # 5. Get the new visual state and append it to the moving stack
        next_state = gamer.get_state()
        state_stack.append(next_state)

        # 6. Draw the game state (we only draw the most recent frame visually)
        gamer.draw()

        # 7. Render the overlay text
        gen_text = font.render(f"Gen: {gen_number}", True, (255, 255, 255))
        score_text = small_font.render(f"Score: {gamer.score}", True, (200, 200, 200))

        bg_rect = pygame.Rect(5, 5, max(gen_text.get_width(), score_text.get_width()) + 10, 70)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(180)
        s.fill((0, 0, 0))
        gamer.screen.blit(s, (5, 5))

        gamer.screen.blit(gen_text, (10, 10))
        gamer.screen.blit(score_text, (10, 45))

        pygame.display.flip()
        gamer.clock.tick(fps)

    print(f"Gen {gen_number} died with Score: {gamer.prev_score}")

print("Showcase Complete.")
pygame.quit()