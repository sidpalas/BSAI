import copy
import random
from time import sleep
import logging
import sys
import os
import numpy as np

# Disable
def disablePrint():
    sys.stdout = open(os.devnull, 'w')

# Enable
def enablePrint():
    sys.stdout = sys.__stdout__

class Game:
    def __init__(self, numPlayers, playerTypes, rows, columns, showDisplay = True):
        self.numPlayers = numPlayers
        self.playerTypes = playerTypes
        self.rows = rows
        self.columns = columns
        self.showDisplay = showDisplay
        if numPlayers == 1:
            trainingPlayer = Player(1, playerTypes[0], rows, columns)
            self.board = PlayerBoard(rows, columns, trainingPlayer, showDisplay)
        elif numPlayers == 2:
            # 2 players (head to head):
            self.board = Board(rows, columns, playerTypes[0], playerTypes[1], showDisplay)
        else:
            raise ValueError

    def playGame(self):
        gameEnd = False
        while not gameEnd:
            gameEnd = self.board.executeTurn()
            sleep(0.01)

    #these methods assume single player board
    #modeled after https://gist.github.com/EderSantana/c7222daa328f0e885093
    def updateState(self, action):
        #action is an int in range(0,row*column)
        position = [action // self.columns, action % self.columns]
        self.board.shoot(position)

    def observe(self):
        return self.board.getGameState()

    def act(self, action):
        self.updateState(action)
        reward = self.board.reward
        gameOver = self.board.isGameOver()
        return self.observe(), reward, gameOver

    def reset(self):
        self.__init__(self.numPlayers, self.playerTypes, self.rows, self.columns, self.showDisplay)



class Board:
    def __init__(self, rows, columns, player1Type = 'AI', player2Type = 'AI', showDisplay = True):
        self.player1 = Player(1, player1Type, rows, columns)
        self.player2 = Player(2, player2Type, rows, columns)
        self.board1 = PlayerBoard(rows, columns, self.player1, showDisplay)
        self.board2 = PlayerBoard(rows, columns, self.player2, showDisplay)
        self.currentPlayer = self.player1
        self.currentBoard = self.board1

    def executeTurn(self):
        gameEnd = self.currentBoard.executeTurn()
        self.currentPlayer = self.player1 if self.currentPlayer.number == 2 else self.player2
        self.currentBoard = self.board1 if self.currentBoard.player.number == 2 else self.board2
        return gameEnd

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


    # def placeShip(self,player, position, length, heading, type):
    #     if player == 1:
    #         self.board1.placeShip(position, length, heading, type)
    #     elif player == 2:
    #         self.board2.placeShip(position, length, heading, type)

class PlayerBoard:
    MISS_VALUE = -1
    HIT_VALUE = 100
    REPEAT_VALUE = -5
    # ships = [2,3,3,4,5]
    # ships = [2,3]
    ships = [2]
    lifeCount = sum(ships)
    numShips = len(ships)

    def __init__(self, rows, columns, player, showDisplay):
        if not showDisplay:
            disablePrint()
        self.lifeCount = PlayerBoard.lifeCount
        self.rows = rows
        self.columns = columns
        self.grid = np.zeros([rows,columns], dtype=int)
        self.randomBoatPlacement()
        self.opponentView = np.zeros([rows,columns],dtype=int)
        self.player = player
        self.ships = PlayerBoard.ships[:] #used to keep track of when a particular boat is sunk
        self.shipsSunk = np.zeros([len(self.ships),], dtype=int)
        self.reward = 0
        self.score = 0
        self.moves = 0

    def isGameOver(self):
        if self.lifeCount == 0:
            enablePrint()
            currentPlayerNum = self.player.number
            print('*'*50)
            print('Player %s Wins by clearing Board %d in %s moves!' % (currentPlayerNum, 1 if currentPlayerNum == 2 else 2, self.moves)) #(which player num is shooting at which board?)
            print('*'*50)
            return True
        else:
            return False

    def executeTurn(self):
        print('\nPlayer %s Turn:' % self.player.number)
        print("#"*20)
        print('\nBefore:')
        print("Ship State: %s" % self.shipsSunk)
        print('Board score: %s' % self.getScore())
        self.printView()
        print('\n')


        # # Initially I was preventing bad shots...
        # validShot = False
        # while not validShot:
        #     validShot = self.isValidShot(shotPosition)

        # # A bad shot will now just be a skipped turn
        shotPosition = self.player.getShot()


        print('Firing at %s' % shotPosition)
        self.shoot(shotPosition)
        print('\nAfter:')
        print("Ship State: %s" % self.shipsSunk)
        print('Board score: %s' % self.getScore())
        self.printView()
        print('\n')
        return self.isGameOver()


    def getGameState(self):
        # gameState = np.concatenate((self.grid.flatten(),self.shipsSunk.flatten()),axis = 0)
        gameState = self.opponentView.flatten()
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

        #check other ships
        if heading == "vertical":
            for i in range(length):
                if self.grid[position[0] + i][position[1]] != 0:
                    print('another boat is there')
                    return False
        elif heading == "horizontal":
            for j in range(length):
                if self.grid[position[0]][position[1] + j] != 0:
                    print('another boat is there')
                    return False
        else:
            raise ValueError

        return True

    def isValidShot(self, position):
        if position[0] not in range(self.rows) or position[1] not in range(self.columns):
            return False
        if self.grid[position[0]][position[1]] >= 0:
            return True
        else:
            # print('invalid shot, try again')
            return False

    def placeShip(self, position, length, heading, type):
        if self.isValidPlacement(position, length, heading):
            startRow = position[0]
            startCol = position[1]
            if heading == 'vertical':
                for i in range(length):
                    self.grid[startRow + i][startCol] = type
            elif heading == 'horizontal':
                for j in range(length):
                    self.grid[startRow][startCol + j] = type
        else:
            print('invalid placement, try again')

    def printBoard(self):
        for row in self.grid:
            print(row)

    def printView(self):
        for row in self.opponentView:
            for col in row:
                print('%3d' % col, end=' ')
            print('')

    def randomBoatPlacement(self):
        for i, ship in enumerate(PlayerBoard.ships):
            length = ship
            type = i + 1
            heading = "vertical" if random.randint(0,1) == 0 else "horizontal"
            validPlacement = False
            while not validPlacement:
                position = [random.randint(0,7),random.randint(0,7)]
                validPlacement = self.isValidPlacement(position, ship, heading)
            self.placeShip(position, length, heading, type)

    def shoot(self, position):
        if self.isValidShot(position):
            self.moves += 1
            val = self.grid[position[0]][position[1]]
            if val == 0:
                print('Miss!')
                self.grid[position[0]][position[1]] = -(PlayerBoard.numShips+1) #+1 to avoid conflict with boat indices
                self.opponentView[position[0]][position[1]]= -1
                reward = PlayerBoard.MISS_VALUE
            else:
                print('Hit!')
                self.grid[position[0]][position[1]] *= -1
                self.opponentView[position[0]][position[1]] = 1
                reward = PlayerBoard.HIT_VALUE
                self.lifeCount -= 1
                self.ships[val-1] -= 1
                if self.ships[val-1] == 0:
                    self.shipsSunk[val-1]=1 #would use True, but using in the gameState variable with ints
                    print('Ship of length ' + str(val) + ' sunk!')

            self.score += reward
            self.reward = reward
            return True
        else:
            reward = PlayerBoard.REPEAT_VALUE
            self.score += reward
            return False

class Player:
    def __init__(self, number, type, rows, columns):
        self.type = type
        self.number = number
        self.rows = rows
        self.columns = columns

    def getShot(self):
        if self.type == 'AI':
            return [random.randint(0,self.rows-1),random.randint(0,self.columns-1)]
        elif self.type == 'Human':
            positionString = input('Player ' + str(self.number) + ' Fire at will (row <space> col, zero indexed) \n')

            #TODO: Add error handling for inputs... add regex

            positionList = list(map(int, positionString.split()))
            return positionList
        else:
            raise ValueError


if __name__ == "__main__":
    testGame = Game(numPlayers = 1, playerTypes = ['AI'], rows=2, columns=2, showDisplay=True)
    # testGame = Game(numPlayers = 2, playerTypes = ['AI']*2, rows=4, columns=4, showDisplay=True)

    testGame.playGame()
