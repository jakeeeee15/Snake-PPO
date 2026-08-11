from game_engine import Engine
from playing_model import FrameStack
import numpy

class Vector_Engine:
    def __init__(self, num=16):
        self.num = num
        self.env = [Engine(model=True) for _ in range(num)]
        self.stacks = [FrameStack() for _ in range(num)]

    def reset(self):
        for i in range(self.num):
            self.env[i].reset()
            state = self.env[i].get_state()
            for _ in range(4):
                self.stacks[i].add(state)

    def get_states(self):    #returns only that frame
        states = []
        for i in range(self.num):
            states.append(self.env[i].get_state())
        return states

    def get_stacks(self):
        stacks =[]
        for i in range(self.num):
            stacks.append(self.stacks[i].stack)
        return numpy.array(stacks, dtype=numpy.float32).reshape((16, 12, 17, 17))

    def add_states(self, states):
        for i in range(self.num):
            self.stacks[i].add(states[i])

    def push_states(self):
        states = self.get_states()
        self.add_states(states)


    def step(self, actions):
        rewards=[]
        dones=[]
        for i in range(self.num):
            reward, done = self.env[i].step(actions[i])
            rewards.append(reward)
            dones.append(done)
            next_state = self.env[i].get_state()
            if dones[i]:
                self.env[i].reset()
                new_state = self.env[i].get_state()
                for _ in range(4):
                    self.stacks[i].add(new_state)
        return rewards, dones


