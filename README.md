# AI agent that finds the best path to the goal while avoiding traps. Uses the Q-Learning algorithm.

##### In this project, we developed model-free learning.
- In this method, the agent does not know the rewards and moves randomly around the world until it reaches the Goal, thus completing an episode.
- After each episode, the Q Learning table is updated. This table contains rewards for each possible action in each possible state, which are calculated from the Goal to the initial position for each episode.
- After all episodes are completed, arrows are marked on the board to indicate the best action to take in each state.

In order to make each episode ‘faster,’ in the client.py file, you can change the sleep_t parameter in the execute method of the Client class and set it to 0.
