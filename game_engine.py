import numpy as np
import pygame
import sys
import random
from collections import deque

pygame.init()

HEIGHT = 510

class Food:
    def __init__(self, snake_body):
        self.snake_body = snake_body
        x = random.randint(0, 16)
        y = random.randint(0, 16)
        while (x, y) in self.snake_body:
            x = random.randint(0, 16)
            y = random.randint(0, 16)
        self.x = x
        self.y = y





class Engine:
    def __init__(self, height=510, grid_size=30, model=False):
        self.height = height
        self.grid_size = grid_size
        self.model=model
        if not model:
            self.screen = pygame.display.set_mode((self.height, self.height))
        self.clock = pygame.time.Clock()
        self.snake_x = random.randint(3, 13)
        self.snake_y = random.randint(3, 13)
        self.snake_length = 3
        self.snake_queue = deque(
            [(self.snake_x - 2, self.snake_y), (self.snake_x - 1, self.snake_y), (self.snake_x, self.snake_y)])
        self.dirn = 2
        self.food = Food(self.snake_queue)
        self.score=0
        self.prev_score=0
        self.steps_without_food = 0

    def reset(self):
        if not self.model:
            self.screen = pygame.display.set_mode((self.height, self.height))
        self.clock = pygame.time.Clock()
        self.snake_x = random.randint(3, 13)
        self.snake_y = random.randint(3, 13)
        self.snake_length = 3
        self.score=0
        self.snake_queue = deque(
            [(self.snake_x - 2, self.snake_y), (self.snake_x - 1, self.snake_y), (self.snake_x, self.snake_y)])
        self.dirn = 2
        self.food = Food(self.snake_queue)
        self.steps_without_food=0

    def step(self, action=0):
        # 0=nothing, 1=left, 2=right, 3=up, 4=down
        done=False
        self.steps_without_food+=1
        reward=-0.02
        if action == 0 or self.dirn == action or (self.dirn == 1 and action == 2) or (
                self.dirn == 2 and action == 1) or (self.dirn == 3 and action == 4) or (self.dirn == 4 and action == 3):
            if self.dirn == 1:
                self.snake_x -= 1
            elif self.dirn == 2:
                self.snake_x += 1
            elif self.dirn == 3:
                self.snake_y -= 1
            elif self.dirn == 4:
                self.snake_y += 1
        else:
            self.dirn = action
            if self.dirn == 1:
                self.snake_x -= 1
            elif self.dirn == 2:
                self.snake_x += 1
            elif self.dirn == 3:
                self.snake_y -= 1
            elif self.dirn == 4:
                self.snake_y += 1
        self.snake_x = int(self.snake_x % (self.height / self.grid_size))
        self.snake_y = int(self.snake_y % (self.height / self.grid_size))
        self.snake_queue.append((self.snake_x, self.snake_y))
        if self.snake_x==self.food.x and self.snake_y==self.food.y:
            self.food = Food(self.snake_queue)
            self.score+=1
            reward=10.0
            self.snake_length+=1
            self.steps_without_food=0
        else:
            self.snake_queue.popleft()
            starve_limit = 150 + (self.snake_length * 10)
            if self.snake_queue.count((self.snake_x, self.snake_y)) > 1 or self.steps_without_food > starve_limit:
                reward = -5.0
                done = True
                self.prev_score = self.score
                self.reset()
        return reward, done


    def get_state(self):
        # 0->nothing 1->snake_body 2->snakehead 3->food
        state = np.zeros((3, 17, 17))
        for (x, y) in self.snake_queue:
            state[git 0][x][y] = 1.0
        state[0][self.snake_x][self.snake_y] = 0.0
        state[1][self.snake_x][self.snake_y] = 1.0
        state[2][self.food.x][self.food.y] = 1.0
        return state


    def draw(self):
        self.screen.fill((9, 9, 59))
        for square in self.snake_queue:
            box = pygame.Rect(square[0] * 30, square[1] * 30, 30, 30)
            pygame.draw.rect(self.screen, (0, 150, 0), box)
        box_head = pygame.Rect(self.snake_x * 30, self.snake_y * 30, 30, 30)
        pygame.draw.rect(self.screen, (150, 75, 0), box_head)

        for i in range(0, HEIGHT, self.grid_size):
            pygame.draw.line(self.screen, (200, 0, 0), (0, i), (HEIGHT, i))
            pygame.draw.line(self.screen, (200, 0, 0), (i, 0), (i, HEIGHT), 1)
        food_box = pygame.Rect(self.food.x*30, self.food.y*30, 30, 30)
        pygame.draw.rect(self.screen, (255, 30, 20), food_box)
        pygame.display.set_caption("Score : " + str(self.score))
        pygame.display.flip()
        self.clock.tick(60)

    def draw_array(self, arr):
        self.screen.fill((9, 9, 59))
        for i, row in enumerate(arr[0]):
            for j, col in enumerate(row):
                if col==1.0:
                    box = pygame.Rect(i * 30, j * 30, 30, 30)
                    pygame.draw.rect(self.screen, (0, 150, 0), box)
        for i, row in enumerate(arr[1]):
            for j, col in enumerate(row):
                if col == 1.0:
                    box_head = pygame.Rect(i * 30, j * 30, 30, 30)
                    pygame.draw.rect(self.screen, (150, 75, 0), box_head)
        for i, row in enumerate(arr[2]):
            for j, col in enumerate(row):
                if col == 1.0:
                    food_box = pygame.Rect(i * 30, j * 30, 30, 30)
                    pygame.draw.rect(self.screen, (255, 30, 20), food_box)

        for i in range(0, HEIGHT, self.grid_size):
            pygame.draw.line(self.screen, (200, 0, 0), (0, i), (HEIGHT, i))
            pygame.draw.line(self.screen, (200, 0, 0), (i, 0), (i, HEIGHT), 1)

        pygame.display.set_caption("Score : " + str(self.score))
        pygame.display.flip()



# --- MAIN LOOP ---
if __name__ == '__main__':
    gamer = Engine()
    running = True

    move_delay = 120  # You can tweak this base speed
    last_move_time = pygame.time.get_ticks()

    state = gamer.get_state()
    gamer.draw_array(state)

    done=False
    while running:
        forced_step = False

        # 1. Catch Inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                action = 0
                if event.key == pygame.K_LEFT:
                    action = 1
                elif event.key == pygame.K_RIGHT:
                    action = 2
                elif event.key == pygame.K_UP:
                    action = 3
                elif event.key == pygame.K_DOWN:
                    action = 4

                if action != 0:
                    # Prevent reversing into itself
                    opposite_dirs = {1: 2, 2: 1, 3: 4, 4: 3}

                    # If it's a valid 90-degree turn, snap the snake immediately!
                    if action != gamer.dirn and action != opposite_dirs.get(gamer.dirn, 0):
                        reward, done = gamer.step(action)
                        last_move_time = pygame.time.get_ticks()  # Reset the timer
                        forced_step = True

        # 2. Auto-move on timer (only if we didn't just force a turn this frame)
        current_time = pygame.time.get_ticks()
        if not forced_step and current_time - last_move_time >= move_delay:
            reward, done = gamer.step(0)
            last_move_time = current_time

        # 3. Render
        if done:
            print("Game Done")
            done=False
            gamer.reset()
        gamer.draw()


    pygame.quit()
    sys.exit()