import torch
from torch import nn
from torch.nn import Module
import torch.nn.functional as F
from torch.distributions import Categorical
from collections import deque
import numpy as np
import random


class PpoModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(12, 16, kernel_size=3, stride=1, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, stride=1)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, stride=1)

        flatten_size = 13*13*64

        self.shared_linear = nn.Linear(flatten_size, 256)

        self.actor_hidden = nn.Linear(256, 128)
        self.actor_out_layer = nn.Linear(128, 3)

        self.critic_hidden = nn.Linear(256, 128)
        self.critic_out_layer = nn.Linear(128, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))

        x = torch.flatten(x, start_dim=1)
        x = F.relu(self.shared_linear(x))


        actor_x = F.relu(self.actor_hidden(x))
        actor_out = self.actor_out_layer(actor_x)

        critic_x = F.relu(self.critic_hidden(x))
        state_value = self.critic_out_layer(critic_x)

        return actor_out, state_value

    def get_action(self, state):
        logits, value = self.forward(state)
        action_dist = Categorical(logits=logits)

        # This is already an int64 tensor sitting on the GPU!
        action_chosen = action_dist.sample()

        return action_chosen, value, action_dist.log_prob(action_chosen), action_dist.entropy()


#make the frame stacker
class FrameStack:
    def __init__(self):
        queue = np.zeros((3, 17, 17))
        self.stack = deque(maxlen=4)
        for _ in range(4):
            self.stack.append(queue)

    def add(self, new_frames):
        self.stack.append(new_frames)


    def show_frames(self):
        for f in self.stack:
            print(f)

    def shuffle(self):
        temp_list = list(self.stack)



if __name__=='__main__':
    frame_stack = FrameStack()
    frame_stack.show_frames()
    print("DONE")
    frame_stack.add(np.ones((3, 17, 17)))
    frame_stack.show_frames()