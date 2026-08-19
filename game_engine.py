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
        self.model = model
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
        self.score = 0
        self.prev_score = 0
        self.steps_without_food = 0

    def reset(self):
        if not self.model:
            self.screen = pygame.display.set_mode((self.height, self.height))
        self.clock = pygame.time.Clock()
        self.snake_x = random.randint(3, 13)
        self.snake_y = random.randint(3, 13)
        self.snake_length = 3
        self.score = 0
        self.snake_queue = deque(
            [(self.snake_x - 2, self.snake_y), (self.snake_x - 1, self.snake_y), (self.snake_x, self.snake_y)])
        self.dirn = 2
        self.food = Food(self.snake_queue)
        self.steps_without_food = 0

    def get_distance(self):
        return abs(self.snake_x - self.food.x) + abs(self.snake_y - self.food.y)

    def step(self, action=0):
        done = False
        self.steps_without_food += 1
        time_penalty = -0.02 * max(0.0, (30 - self.snake_length) / 30.0)
        reward = time_penalty
        # dist_before = self.get_distance()

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

        grid_max = int(self.height / self.grid_size)

        if self.snake_x < 0 or self.snake_x >= grid_max or self.snake_y < 0 or self.snake_y >= grid_max:
            reward = -5.0 - (self.snake_length * 0.2)
            done = True
            self.prev_score = self.score
            self.reset()
            return reward, done

        self.snake_queue.append((self.snake_x, self.snake_y))

        # dist_after = self.get_distance()
        # reward=-0.01
        # if dist_after < dist_before:
        #     reward = 0.05
        # else:
        #     reward = -0.05

        if self.snake_x == self.food.x and self.snake_y == self.food.y:
            self.food = Food(self.snake_queue)
            self.score += 1
            reward = 10.0
            self.snake_length += 1
            self.steps_without_food = 0
        else:
            self.snake_queue.popleft()

            dynamic_starvation_limit = 200 + (self.snake_length * 3)

            if self.snake_queue.count(
                    (self.snake_x, self.snake_y)) > 1 or self.steps_without_food > dynamic_starvation_limit:
                reward = -5.0 - (self.snake_length * 0.2)
                done = True
                self.prev_score = self.score
                self.reset()

        return reward, done

    def model_step(self, action=0):
        if action == 0:
            abs_action = self.dirn
        elif action == 1:
            left_turn_map = {1: 4, 2: 3, 3: 1, 4: 2}
            abs_action = left_turn_map[self.dirn]
        elif action == 2:
            right_turn_map = {1: 3, 2: 4, 3: 2, 4: 1}
            abs_action = right_turn_map[self.dirn]
        else:
            abs_action = self.dirn

        return self.step(abs_action)

    def get_state(self):
        state = np.zeros((3, 17, 17))
        body_length = len(self.snake_queue)

        for i, (x, y) in enumerate(self.snake_queue):
            if 0 <= x < 17 and 0 <= y < 17:
                state[0][x][y] = (i + 1) / body_length

        if 0 <= self.snake_x < 17 and 0 <= self.snake_y < 17:
            state[0][self.snake_x][self.snake_y] = 0.0
            state[1][self.snake_x][self.snake_y] = 1.0

        if 0 <= self.food.x < 17 and 0 <= self.food.y < 17:
            state[2][self.food.x][self.food.y] = 1.0

        return state

    def draw(self):
        self.screen.fill((9, 9, 59))
        for square in self.snake_queue:
            box = pygame.Rect(square[0] * 30, square[1] * 30, 30, 30)
            pygame.draw.rect(self.screen, (0, 150, 0), box)
        box_head = pygame.Rect(self.snake_x * 30, self.snake_y * 30, 30, 30)
        pygame.draw.rect(self.screen, (150, 75, 0), box_head)

        for i in range(0, HEIGHT + 1, self.grid_size):
            pygame.draw.line(self.screen, (200, 0, 0), (0, i), (HEIGHT, i))
            pygame.draw.line(self.screen, (200, 0, 0), (i, 0), (i, HEIGHT), 1)
        food_box = pygame.Rect(self.food.x * 30, self.food.y * 30, 30, 30)
        pygame.draw.rect(self.screen, (255, 30, 20), food_box)
        pygame.display.set_caption("Score : " + str(self.score))
        pygame.display.flip()
        self.clock.tick(60)

    def draw_array(self, arr):
        self.screen.fill((9, 9, 59))
        for i, row in enumerate(arr[0]):
            for j, col in enumerate(row):
                if col > 0.0:
                    box = pygame.Rect(i * 30, j * 30, 30, 30)
                    pygame.draw.rect(self.screen, (0, int(150 * col), 0), box)
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

        for i in range(0, HEIGHT + 1, self.grid_size):
            pygame.draw.line(self.screen, (200, 0, 0), (0, i), (HEIGHT, i))
            pygame.draw.line(self.screen, (200, 0, 0), (i, 0), (i, HEIGHT), 1)

        pygame.display.set_caption("Score : " + str(self.score))
        pygame.display.flip()


if __name__ == '__main__':
    gamer = Engine()
    running = True

    move_delay = 120
    last_move_time = pygame.time.get_ticks()

    state = gamer.get_state()
    gamer.draw_array(state)

    done = False

    while running:
        forced_step = False

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
                    opposite_dirs = {1: 2, 2: 1, 3: 4, 4: 3}
                    if action != gamer.dirn and action != opposite_dirs.get(gamer.dirn, 0):
                        reward, done = gamer.step(action)
                        last_move_time = pygame.time.get_ticks()
                        forced_step = True

        current_time = pygame.time.get_ticks()
        if not forced_step and current_time - last_move_time >= move_delay:
            reward, done = gamer.step(0)
            last_move_time = current_time

        if done:
            print("Game Done")
            done = False
            gamer.reset()

        gamer.draw()

    pygame.quit()
    sys.exit()