import copy
import random
from time import sleep
import logging
import sys
import os

# Disable
def disablePrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__



class Board:
    def __init__(self, rows, columns, player1Type = 'AI', player2Type = 'AI', showDisplay = True):
        self.player1 = Player(1, player1Type)
        self.player2 = Player(2, player2Type)
        self.board1 = PlayerBoard(rows, columns, self.player1, showDisplay)
        self.board2 = PlayerBoard(rows, columns, self.player2, showDisplay)
        self.currentPlayer = self.player1
        self.currentBoard = self.board1

    # def checkGameEnd(self):
    #     return self.currentBoard.checkGameEnd()

    def executeTurn(self):
        gameEnd = self.currentBoard.executeTurn()
        print('Board 1 Score: %s, Board 2 Score: %s' % (self.board1.getScore(), self.board2.getScore()))
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
    HIT_VALUE = 10
    ships = [2,3,3,4,5]
    lifeCount = sum(ships)
    numShips = len(ships)

    def __init__(self, rows, columns, player, showDisplay):
        if not showDisplay:
            disablePrint()
        self.lifeCount = PlayerBoard.lifeCount
        self.rows = rows
        self.columns = columns
        self.grid = [[0]*columns for i in range(rows)]
        self.randomBoatPlacement()
        self.opponentView = [[0]*columns for i in range(rows)]
        self.player = player
        self.ships = PlayerBoard.ships[:] #used to keep track of when a particular boat is sunk
        self.shipsSunk = [0]*len(self.ships)
        self.gameState = [item for sublist in self.grid for item in sublist] + self.shipsSunk
        self.score = 0


    def checkGameEnd(self):
        if self.lifeCount == 0:
            enablePrint()
            currentPlayerNum = self.player.number
            print('Player %s Wins by clearing Board %d!' % (currentPlayerNum, 1 if currentPlayerNum == 2 else 2)) #(which player num is shooting at which board?)
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
        validShot = False
        while not validShot:
            shotPosition = self.player.getShot()
            validShot = self.isValidShot(shotPosition)
        print('Firing at %s' % shotPosition)
        self.shoot(shotPosition)

        print("Ship State: %s" % self.shipsSunk)
        print('\nAfter:')
        print(self.shipsSunk)
        print('Board score: %s' % self.getScore())
        self.printView()
        print('\n')
        return self.checkGameEnd()


    def getGameState(self):
        flatBoard = [item for sublist in self.opponentView for item in sublist]
        return flatBoard + self.shipsSunk

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

    #need to keep track of individual ships to be able to know when one is sunk...
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
            val = self.grid[position[0]][position[1]]
            if val == 0:
                print('Miss!')
                self.grid[position[0]][position[1]] = -(PlayerBoard.numShips+1) #+1 to avoid conflict with boat indices
                self.opponentView[position[0]][position[1]]= PlayerBoard.MISS_VALUE
                self.score += PlayerBoard.MISS_VALUE
            else:
                print('Hit!')
                self.grid[position[0]][position[1]] *= -1
                self.opponentView[position[0]][position[1]] = PlayerBoard.HIT_VALUE
                self.score += PlayerBoard.HIT_VALUE
                self.lifeCount -= 1
                self.ships[val-1] -= 1
                if self.ships[val-1] == 0:
                    self.shipsSunk[val-1]=1 #would use True, but using in the gameState variable with ints
                    print('Ship of length ' + str(val) + ' sunk!')
            return True
        else:
            return False

class Player:
    def __init__(self, number, type = 'AI'):
        self.type = type
        self.number = number

    def getShot(self):
        if self.type == 'AI':
            return [random.randint(0,7),random.randint(0,7)]
        elif self.type == 'Human':
            positionString = input('Player ' + str(self.number) + ' Fire at will (row <space> col, zero indexed) \n')

            #TODO: Add error handling for inputs... add regex

            positionList = list(map(int, positionString.split()))
            return positionList
        else:
            raise ValueError


if __name__ == "__main__":
    # 2 players (head to head):
    testBoard = Board(rows = 8, columns = 8, player1Type = 'AI', player2Type = 'AI', showDisplay = True)
    gameEnd = False
    i = 0
    while not gameEnd:
        gameEnd = testBoard.executeTurn()
        # sleep(0.01)


    ############'

    # # 1 Player (training)
    trainingPlayer = Player(1, 'AI')
    trainingBoard = PlayerBoard(rows = 8, columns = 8, player = trainingPlayer, showDisplay = False)
    gameEnd = False
    while not gameEnd:
        gameEnd = trainingBoard.executeTurn()
        # sleep(0.01)
