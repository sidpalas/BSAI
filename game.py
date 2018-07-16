import copy
import random
from time import sleep


class Board:
    def __init__(self, rows, columns):
        self.board1 = PlayerBoard(rows, columns)
        self.board2 = PlayerBoard(rows, columns)
        self.board1.randomBoatPlacement()
        self.board2.randomBoatPlacement()

    def printBoard(self):
        print('\n')
        self.board1.printBoard()
        print('#'*40)
        self.board2.printBoard()
        print('\n')

    def printView(self):
        print('\n')
        self.board1.printView()
        print('#'*40)
        self.board2.printView()
        print('\n')

    def shoot(self, player, auto = True):
        validShot = False
        while not validShot:
            if auto:
                positionList = [random.randint(0,7), random.randint(0,7)]
            else:
                positionString = input('Player ' + str(player) + ' Fire at will (row <space> col, zero indexed) \n')
                #error handling for inputs... add regex
                positionList = list(map(int, positionString.split()))
            if player == 1:
                validShot = self.board1.isValidShot(positionList)
            else:
                validShot = self.board2.isValidShot(positionList)
        if player == 1:
            self.board1.shoot(positionList)
        elif player == 2:
            self.board2.shoot(positionList)

    def placeShip(self,player, position, length, heading, type):
        if player == 1:
            self.board1.placeShip(position, length, heading, type)
        elif player == 2:
            self.board2.placeShip(position, length, heading, type)

    def checkGameEnd(self):
        if self.board1.lifeCount == 0:
            print('Player 2 Wins!')
            return True
        elif self.board2.lifeCount == 0:
            print('Player 1 Wins!')
            return True
        else:
            return False

class PlayerBoard:
    boats = [2,3,3,4,5]

    def __init__(self, rows, columns):
        self.lifeCount = 17
        self.rows = rows
        self.columns = columns
        self.grid = [[0]*columns for i in range(rows)]
        self.opponentView = [[' ']*columns for i in range(rows)]

    def randomBoatPlacement(self):
        for i, boat in enumerate(PlayerBoard.boats):
            length = boat
            type = i + 1
            heading = "vertical" if random.randint(0,1) == 0 else "horizontal"
            validPlacement = False
            while not validPlacement:
                position = [random.randint(0,7),random.randint(0,7)]
                validPlacement = self.isValidPlacement(position, boat, heading)
            self.placeShip(position, length, heading, type)

    def printBoard(self):
        for row in self.grid:
            print(row)

    def printView(self):
        for row in self.opponentView:
            print(row)

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


    #need to keep track of individual ships to be able to know when one is sunk...

    def isValidShot(self, position):
        if self.grid[position[0]][position[1]] >= 0:
            return True
        else:
            print('invalid shot, try again')
            return False


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

        return True

    def shoot(self, position):
        if self.isValidShot(position):
            val = self.grid[position[0]][position[1]]
            if val == 0:
                print('Miss!')
                self.grid[position[0]][position[1]] = -9
                self.opponentView[position[0]][position[1]]='O'
            else:
                print('Hit!')
                self.grid[position[0]][position[1]] *= -1
                self.opponentView[position[0]][position[1]] = 'X'
                self.lifeCount -= 1
            return True
        else:
            return False

class Ship:
    def __init__(self, length):
        self.length = length



testBoard = Board(8,8)

i = 0
while not testBoard.checkGameEnd():
    playerNum = i % 2 + 1
    testBoard.shoot(playerNum)
    testBoard.printBoard()
    testBoard.printView()
    i += 1
    sleep(0.1) # Time in seconds.
