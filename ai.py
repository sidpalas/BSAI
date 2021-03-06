import json
import numpy as np
import logging
from keras.models import Sequential
# from keras.layers.convolutional import Convolution2D, MaxPooling2D

from keras.layers import Dense, Dropout, Conv2D, Conv1D
from keras.optimizers import sgd

import matplotlib.pyplot as plt


from game import Game

# Implementation based on https://edersantana.github.io/articles/keras_rl/
# More description here https://ai.intel.com/demystifying-deep-reinforcement-learning/

class ExperienceReplay(object):
    def __init__(self, max_memory=100, discount=.9):
        self.max_memory = max_memory
        self.memory = list()
        self.discount = discount

    def remember(self, states, game_over):
        # memory[i] = [[state_t, action_t, reward_t, state_t+1], game_over?]
        self.memory.append([states, game_over])
        if len(self.memory) > self.max_memory:
            del self.memory[0]

    def get_batch(self, model, batch_size=10):
        len_memory = len(self.memory)
        num_actions = model.output_shape[-1]
        env_dim = self.memory[0][0][0].shape[1]
        inputs = np.zeros((min(len_memory, batch_size), env_dim))
        targets = np.zeros((inputs.shape[0], num_actions))
        for i, idx in enumerate(np.random.randint(0, len_memory,
                                                  size=inputs.shape[0])):
            state_t, action_t, reward_t, state_tp1 = self.memory[idx][0]
            game_over = self.memory[idx][1]

            inputs[i:i+1] = state_t
            # There should be no target values for actions not taken.
            # Thou shalt not correct actions not taken #deep
            targets[i] = model.predict(state_t)[0]
            Q_sa = np.max(model.predict(state_tp1)[0])
            if game_over:  # if game_over is True
                targets[i, action_t] = reward_t
            else:
                # reward_t + gamma * max_a' Q(s', a')
                targets[i, action_t] = reward_t + self.discount * Q_sa
        return inputs, targets

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    # parameters
    epsilon = .1  # exploration
    epoch = 300
    max_memory = 1
    discount = 0 #future moves don't really get benefit from current move
    hidden_size = 150
    batch_size = 10
    grid_size = 8
    num_actions = grid_size**2  # anywhere in grid

    model = Sequential()
    # model.add(Conv2D(64, 3,
    #     data_format='channels_last',
    # 	input_shape = (grid_size, grid_size, 1,),
    # 	activation='relu',
    #     padding = 'same')) #cant get input dimensions to agree...
    model.add(Dense(hidden_size, input_shape=(grid_size**2,), activation='relu'))
    model.add(Dense(hidden_size, activation='relu'))
    model.add(Dense(hidden_size//2, activation='relu'))
    model.add(Dense(num_actions))
    model.compile(sgd(lr=.05), "mse")

    # model.add(Dropout(0.5))

    # If you want to continue training from a previous model, just uncomment the line bellow
    # model.load_weights("model.h5")

    # Define environment/game
    env = Game(numPlayers = 1, playerTypes = ['AI'], rows=grid_size, columns=grid_size, ships = [2,3,3,4,5], showDisplay=False)

    # Initialize experience replay object
    exp_replay = ExperienceReplay(max_memory=max_memory,discount = discount)

    turnNums = []

    # Train
    for e in range(epoch):
        loss = 0.
        env.reset()
        game_over = False
        # get initial input
        input_t = env.observe()
        turnNum = 0
        while not game_over:
            input_tm1 = input_t

            # get next action
            if np.random.rand() <= epsilon:
                # action = np.random.randint(0, num_actions)
                validPosition = False
                while not validPosition:
                    action = np.random.randint(0, num_actions)
                    position = [action // env.columns, action % env.columns]
                    validPosition = env.board.isValidShot(position)
            else:
                q = model.predict(input_tm1)
                # action = np.argmax(q[0])
                qSortedDescending = np.argsort(q[0])[::-1]
                i = 0
                validPosition = False
                while not validPosition:
                    action = qSortedDescending[i]
                    position = [action // env.columns, action % env.columns]
                    validPosition = env.board.isValidShot(position)
                    i += 1


            # apply action, get rewards and new state
            input_t, reward, game_over = env.act(action)

            # store experience
            exp_replay.remember([input_tm1, action, reward, input_t], game_over)

            # adapt model
            inputs, targets = exp_replay.get_batch(model, batch_size=batch_size)

            loss += model.train_on_batch(inputs, targets)
            turnNum += 1
        print("Epoch {:03d}/{} | Loss {:.4f} | Turn count: {}".format(e, epoch-1, loss, turnNum))
        turnNums.append(turnNum)

    plt.plot(turnNums)
    plt.ylabel('Turns to finish game')
    plt.show()

    # Save trained model weights and architecture, this will be used by the visualization code
    model.save_weights("model.h5", overwrite=True)
    with open("model.json", "w") as outfile:
        json.dump(model.to_json(), outfile)
