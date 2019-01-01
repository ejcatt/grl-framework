import grl
import numpy as np
import collections

class BlindMaze(grl.foundations.Domain):

    def react(self, action):    
        e = self.pm.perception(self.sm.transit(action))
        return e

    def setup(self):
        self.maze_len = self.kwargs.get('maze_len', 4)
        self.sm.states = [(x,y) for x in range(self.maze_len) for y in range(self.maze_len)]
        self.am.actions = ['u', 'd', 'l', 'r']
        self.sm.state = self.sm.states[np.random.choice(len(self.sm.states))]

    def transition_func(self, state, action):
        if action == 'u':
            s_nxt = (state[0], min(state[1] + 1, self.maze_len - 1))
        elif action == 'd':
            s_nxt = (state[0], max(state[1] - 1, 0))
        elif action == 'l':
            s_nxt = (max(state[0] - 1, 0), state[1])
        elif action == 'r':
            s_nxt = (min(state[0] + 1, self.maze_len - 1), state[1])
        else:
            s_nxt = state
        return s_nxt
    
    def emission_func(self, state):
        if state == (0,0):
            return ('@', 1)
        else:
            return ('@', 0)
    
    def reward_func(self, h, a, e_nxt, s=None, s_nxt=None):
        return e_nxt[1]


    def reset(self):
        self.sm.state = self.sm.states[np.random.choice(len(self.sm.states))]

class RandomAgent(grl.foundations.Agent):

    def act(self, percept):
        a = np.random.choice(self.am.actions)
        #self.hm.extend_history(a, complete=True)
        return a
    
class GreedyQAgent(grl.foundations.Agent):

    def setup(self):
        self.epsilon = self.kwargs.get('exploration_factor', 0.1)
        self.g = self.kwargs.get('discount_factor', 0.999)
        self.Q = grl.learning.Storage(dims=2, default_val=self.kwargs.get('Q_init', (1,1)), persist=self.kwargs.get('Q_persist', False))
        self.alpha = grl.learning.Storage(dims=2, default_val=self.kwargs.get('learning_rate_init', (0.999, 0.999)))
    
    def interact(self, domain):
        super().interact(domain)
        self.Q.default_argument = collections.deque(self.am.actions)

    def act(self, percept):
        # This is not the first percept received from the domain.
        # This part looks ugly.
        if self.am.action: 
            self.learn(percept)

        a_nxt = [self.Q[percept].argmax(), self.am.actions[np.random.choice(len(self.am.actions))]]

        self.am.action = a_nxt[np.random.choice(2, p=[1-self.epsilon, self.epsilon])]
        return self.am.action
    
    def learn(self, e_nxt):
        a = self.am.action
        e = self.hm.mapped_state()
        self.Q[e][a] = self.Q[e][a] + self.alpha[e][a] * (self.rm.r(self.hm.history, a, e_nxt) + self.g * self.Q[e][a] - self.Q[e_nxt].max())
        self.alpha[e][a] = self.alpha[e][a] ** 2


################################################################

# scenario 1:
# A <- dummy_e
# A -> a

# need to define these two

# A(a|empty) ~ A_0(a)
# E(e|empty,a)

# The agent can not do better than a random agent in the start, unless it has some prior knowledge/model
# of the domain.
# One the otherhand, humans do not act first. But in this situation, the world is not a purely reactive
# simulator, or is it? The act of "doing nothing" is a valid action in the real-world.

# scenario 2:
# E <- dummy_a
# E -> e

# E(e|empty, empty) ~ E_0(e)
# A(a|e)

# The scenario 2 is more typical where there is an initial distributions on the percepts 
# (or intern on states.)


##############################################################

def phi(h):
    # extract last percept
    return h[-1][-1]

history_mgr = grl.managers.HistoryManager(MAX_LENGTH=10, state_map=phi)
domain = BlindMaze(history_mgr)
#agent = RandomAgent(history_mgr)
agent = GreedyQAgent(history_mgr)


a = None 
# The iteration starts from the domain, which is more natural. The domain
# can set the initial state (if any) that consequently sets the initial percept.
agent.interact(domain)

for t in range(50):
    history_mgr.extend_history(a, complete=False)
    e = domain.react(a)
    history_mgr.extend_history(e, complete=True)
    a = agent.act(e)

print(agent.Q)
#print(history_mgr.history)

# a = grl.learning.Storage(dims=3, persist=False)
# print(a[3][1][2] != a[3][1][2])
# print(a[2][1][1] != a[2][1][1])
# a[1][3][4] = 1.5
# print(a[1][3][4] == 1.5)
# print(a[1][3].max() == 1.5)
# print(a[1][3].argmax() == 4)
# print(len(a) == 1)

# b = grl.learning.Storage(persist=True)
# print(b[2][(1,2)] == b[2][(1,2)])
# b[1][3] = 2
# b[1][4] = 4
# print(b[1][3] == 2)
# print(b[1].expectation() == 3.0)
# print(b[1].expectation({3: 1.0, 4:0.0}) == 2.0)
# print(b[1].max() == 4)
# print(b[1].argmax() == 4)
# print(len(b) == 2)
# print(b[5].argmax())
# print(b[7].argmin())

