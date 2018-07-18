import sys
import os
import logging
import argparse
import numpy as np
from random import randint
from time import sleep
import matplotlib.pyplot as plt
import statistics


from ruleBasedAI import RuleAI

# Disable
def disablePrint():
    sys.stdout = open('logFile', 'w')
    # sys.stdout = open(os.devnull, 'w')

# Enable
def enablePrint():
    sys.stdout = sys.__stdout__

class GameBatch:
    def __init__(self, numPlayers, playerTypes, numGames, rows, columns, ships, showDisplay):
        self.numGames = numGames
        self.rows = rows
        self.columns = columns
        self.ships = ships
        self.showDisplay = showDisplay
        self.numPlayers = numPlayers
        self.playerTypes = playerTypes
        return

    def playGames(self):
        winner = []
        numMoves = []
        for i in range(self.numGames):
            thisGame = Game(self.numPlayers, self.playerTypes, self.rows, self.columns, self.ships, self.showDisplay)
            gameReport = thisGame.playGame()
            # print(gameReport)
            if i % 10 == 0:
                print('Game %s of %s' % (i, self.numGames))
            winner.append(gameReport['winnerPlayerNum'])
            numMoves.append(gameReport['winnerNumMoves'])

        gameNum = range(self.numGames)
        meanMoves = statistics.mean(numMoves)

        player2Indices = [i for i, x in enumerate(winner) if x == 2]

        plt.plot(gameNum,numMoves, '^')
        for idx in player2Indices:
            plt.plot(idx,numMoves[idx], 'r^')

        plt.axis([0, self.numGames,0, self.rows*self.columns])
        plt.ylabel('Number of Moves to Win (mean: %s)' % meanMoves)
        plt.xlabel('Game Number')
        plt.show()





class Game:
    def __init__(self, numPlayers, playerTypes, rows, columns, ships, showDisplay):
        self.numPlayers = numPlayers
        self.playerTypes = playerTypes
        self.ships = ships
        self.rows = rows
        self.columns = columns
        self.showDisplay = showDisplay
        if numPlayers == 1:
            trainingPlayer = Player(1, playerTypes[0], rows, columns)
            self.board = PlayerBoard(rows, columns, trainingPlayer, ships, showDisplay)
        elif numPlayers == 2:
            # 2 players (head to head):
            self.board = Board(rows, columns, playerTypes[0], playerTypes[1], ships, showDisplay)
        else:
            raise ValueError

    def playGame(self):
        gameEnd = False
        while not gameEnd:
            gameEnd = self.board.executeTurn()
            # sleep(0.01)
        return self.board.getGameReport()

    #these methods assume single player board
    #modeled after https://gist.github.com/EderSantana/c7222daa328f0e885093
    def updateState(self, action):
        #action[0] is an int in range(0,row*column)
        position = [action // self.columns, action % self.columns]
        self.board.shoot(position)

    def observe(self):
        self.board.printView()
        return self.board.getGameState()

    def act(self, action):
        self.updateState(action)
        reward = self.board.reward
        gameOver = self.board.isGameOver()
        return self.observe(), reward, gameOver

    def reset(self):
        self.__init__(self.numPlayers, self.playerTypes, self.rows, self.columns, self.ships, self.showDisplay)


class Board:
    def __init__(self, rows, columns, player1Type, player2Type, ships, showDisplay):
        self.player1 = Player(1, player1Type, rows, columns)
        self.player2 = Player(2, player2Type, rows, columns)
        self.board1 = PlayerBoard(rows, columns, self.player1, ships, showDisplay)
        self.board2 = PlayerBoard(rows, columns, self.player2, ships, showDisplay)
        self.currentPlayer = self.player1
        self.currentBoard = self.board1

    def executeTurn(self):
        gameEnd = self.currentBoard.executeTurn()
        if gameEnd:
            self.winningBoard = self.currentBoard
        self.currentPlayer = self.player1 if self.currentPlayer.number == 2 else self.player2
        self.currentBoard = self.board1 if self.currentBoard.player.number == 2 else self.board2
        return gameEnd

    def getGameReport(self):
        return self.winningBoard.gameReport

    def printBoard(self):
        print('\n')
        self.board1.printBoard()
        print('#'*32)
        self.board2.printBoard()
        print('\n')

    def printFullView(self):
        print('\n')
        print("Ship State:", self.board1.shipsSunk)
        print('\n')
        self.board1.printView()
        print('#'*32)
        self.board2.printView()
        print('\n')
        print("Ship State:", self.board2.shipsSunk)
        print('\n')

class PlayerBoard:
    MISS_VALUE = -1
    HIT_VALUE = 2
    REPEAT_VALUE = -2
    DISPLAY_MAPPING= {-1:'O', 0:' ', 1:'X'}

    def __init__(self, rows, columns, player, ships, showDisplay):
        if not showDisplay:
            disablePrint()
        self.lifeCount = sum(ships)
        self.numShips = len(ships)
        self.ships = np.array(ships[:], dtype=int) #used to keep track of when a particular boat is sunk
        self.shipsSunk = np.zeros([len(self.ships),], dtype=int)
        self.rows = rows
        self.columns = columns
        self.grid = np.zeros([rows,columns], dtype=int)
        self.randomBoatPlacement()
        self.opponentView = np.zeros([rows,columns],dtype=float)
        self.player = player
        self.reward = 0
        self.score = 0
        self.moves = 0

    def isGameOver(self):
        if self.lifeCount == 0:
            enablePrint()
            currentPlayerNum = self.player.number
            self.gameReport = {'winnerPlayerNum': currentPlayerNum,
                                'winnerNumMoves': self.moves}
            # print('*'*50)
            # print('Player %s Wins by clearing Board %d in %s moves!' % (currentPlayerNum, 1 if currentPlayerNum == 2 else 2, self.moves)) #(which player num is shooting at which board?)
            # print('*'*50)
            return True
        else:
            return False

    def getGameReport(self):
        return self.gameReport

    def executeTurn(self):
        print('\nPlayer %s Turn:' % self.player.number)
        print("#"*20)
        print('\nBefore:')
        print("Ship State: %s" % self.shipsSunk)
        print('Board score: %s' % self.getScore())
        self.printView()
        print('\n')

        # # Repeat shots allowed to retry
        validShot = False
        while not validShot:
            shotPosition = self.player.getShot()
            validShot = self.isValidShot(shotPosition)

        # # Alternatively a bad shot could just be a skipped turn
        # shotPosition = self.player.getShot()


        print('Firing at %s' % shotPosition)
        isHit = self.shoot(shotPosition)
        self.player.postExecution(shotPosition, isHit)
        print('\nAfter:')
        print("Ship State: %s" % self.shipsSunk)
        print('Board score: %s' % self.getScore())
        self.printView()
        print('\n')
        return self.isGameOver()


    def getGameState(self):
        # gameState = np.concatenate((self.grid.flatten(),self.shipsSunk.flatten()),axis = 0)
        gameState = self.opponentView.reshape(1,self.rows*self.columns,)
        return gameState

    def getScore(self):
        return self.score


    def isValidPlacement(self, position, length, heading):
        #check edges
        if position[0] not in range(self.rows) or position[1] not in range(self.columns):
            print('start position out of bounds')
            return False
        if heading == "vertical":
            remainingRows = self.rows - position[0]
            if length > remainingRows:
                print('end position out of bounds')
                return False
        elif heading == "horizontal":
            remainingColumns = self.columns - position[1]
            if length > remainingColumns:
                print('end position out of bounds')
                return False
        else:
            raise ValueError

        #check other ships
        if heading == "vertical":
            for i in range(length):
                if self.grid[position[0] + i, position[1]] != 0:
                    print('another boat is there')
                    return False
        elif heading == "horizontal":
            for j in range(length):
                if self.grid[position[0], position[1] + j] != 0:
                    print('another boat is there')
                    return False
        else:
            raise ValueError

        return True

    def isValidShot(self, position):
        if position[0] not in range(self.rows) or position[1] not in range(self.columns):
            return False
        if self.grid[position[0],position[1]] >= 0:
            return True
        else:
            print('invalid shot, try again')
            return False

    def placeShip(self, position, length, heading, type):
        if self.isValidPlacement(position, length, heading):
            startRow = position[0]
            startCol = position[1]
            if heading == 'vertical':
                for i in range(length):
                    self.grid[startRow + i,startCol] = type
            elif heading == 'horizontal':
                for j in range(length):
                    self.grid[startRow, startCol + j] = type
        else:
            print('invalid placement, try again')

    def printBoard(self):
        for row in self.grid:
            print(row)

    def printView(self):
        print('-'*32)
        for row in self.opponentView:
            print('|', end='')
            for col in row:
                print(' %1s |' % PlayerBoard.DISPLAY_MAPPING[col], end='')
            print('\n'+'-'*32)

    def randomBoatPlacement(self):
        for i, ship in enumerate(self.ships):
            length = ship
            type = i + 1
            validPlacement = False
            while not validPlacement:
                heading = "vertical" if randint(0,1) == 0 else "horizontal"
                position = [randint(0,self.rows-1),randint(0,self.columns-1)]
                validPlacement = self.isValidPlacement(position, ship, heading)
            self.placeShip(position, length, heading, type)

    def shoot(self, position):
        if self.isValidShot(position):
            self.moves += 1
            val = self.grid[position[0],position[1]]
            if val == 0:
                print('Miss!')
                self.grid[position[0],position[1]] = -(self.numShips+1) #+1 to avoid conflict with boat indices
                self.opponentView[position[0],position[1]] = -1
                self.reward = PlayerBoard.MISS_VALUE
                return False
            else:
                print('Hit!')
                self.grid[position[0],position[1]] *= -1
                self.opponentView[position[0],position[1]] = 1
                self.reward = PlayerBoard.HIT_VALUE
                self.score += self.reward
                self.lifeCount -= 1
                self.ships[val-1] -= 1
                if self.ships[val-1] == 0:
                    self.shipsSunk[val-1]=1 #would use True, but using in the gameState variable with ints
                    print('Ship of length ' + str(val) + ' sunk!')
                return True
        else:
            self.reward = PlayerBoard.REPEAT_VALUE
            self.score += self.reward
            return False

class Player:
    def __init__(self, number, playerType, rows, columns):
        self.playerType = playerType
        self.number = number
        self.rows = rows
        self.columns = columns
        self.ai = RuleAI(rows, columns, playerType)

    def getShot(self):
        if self.playerType in ['AI', 'RANDOM']:
            return self.ai.getNextMove()
        elif self.playerType == 'Human':
            positionString = input('Player ' + str(self.number) + ' Fire at will (row <space> col, zero indexed) \n')
            #TODO: Add error handling for inputs
            positionList = list(map(int, positionString.split()))
            return positionList
        else:
            raise ValueError

    def postExecution(self, prevMove, isHit):
        if self.playerType == 'AI':
            self.ai.postExecution(prevMove, isHit)
        else:
            pass



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Play the game.')
    parser.add_argument('--players', metavar='N', type=str, nargs='+', default=['AI', 'AI'],
                            help='')

    args = parser.parse_args()

    if len(args.players)==1:
        testGame = Game(numPlayers = 1, playerTypes = args.players, rows=8, columns=8, ships = [2,3,3,4,5], showDisplay=True)
    else:
        testGame = Game(numPlayers = 2, playerTypes = args.players, rows=8, columns=8, ships = [2,3,3,4,5], showDisplay=True)

    testGame.playGame()
