import copy
import random
from time import sleep

class Board:
    def __init__(self, rows, columns, player1Type = 'AI', player2Type = 'AI'):
        self.player1 = Player(1, player1Type)
        self.player2 = Player(2, player2Type)
        self.board1 = PlayerBoard(rows, columns, self.player1)
        self.board2 = PlayerBoard(rows, columns, self.player2)
        self.board1.randomBoatPlacement()
        self.board2.randomBoatPlacement()
        self.currentPlayer = self.player1
        self.currentBoard = self.board1

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

    # def placeShip(self,player, position, length, heading, type):
    #     if player == 1:
    #         self.board1.placeShip(position, length, heading, type)
    #     elif player == 2:
    #         self.board2.placeShip(position, length, heading, type)

    def checkGameEnd(self):
        return self.currentBoard.checkGameEnd()

    def executeTurn(self):
        self.currentBoard.executeTurn()
        gameEnd = self.checkGameEnd()
        self.currentPlayer = self.player1 if self.currentPlayer.number == 2 else self.player2
        self.currentBoard = self.board1 if self.currentBoard.player.number == 2 else self.board2
        return gameEnd

class PlayerBoard:
    ships = [2,3,3,4,5]
    lifeCount = sum(ships)
    numShips = len(ships)

    def __init__(self, rows, columns, player):
        self.lifeCount = PlayerBoard.lifeCount
        self.rows = rows
        self.columns = columns
        self.grid = [[0]*columns for i in range(rows)]
        self.opponentView = [[' ']*columns for i in range(rows)]
        self.player = player
        self.ships = PlayerBoard.ships[:] #used to keep track of when a particular boat is sunk
        self.shipsSunk = [False]*len(self.ships)

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
        if position[0] not in range(self.rows) or position[1] not in range(self.columns):
            return False
        if self.grid[position[0]][position[1]] >= 0:
            return True
        else:
            # print('invalid shot, try again')
            return False

    def checkGameEnd(self):
        if self.lifeCount == 0:
            print('Player ' + str(self.player.number % 2 + 1) + ' Wins! (which player num is shooting at which board?)')
            return True
        else:
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
        else:
            raise ValueError

        return True

    def shoot(self, position):
        if self.isValidShot(position):
            val = self.grid[position[0]][position[1]]
            if val == 0:
                print('Miss!')
                self.grid[position[0]][position[1]] = -(PlayerBoard.numShips+1) #+1 to avoid conflict with boat indices
                self.opponentView[position[0]][position[1]]='O'
            else:
                print('Hit!')
                self.grid[position[0]][position[1]] *= -1
                self.opponentView[position[0]][position[1]] = 'X'
                self.lifeCount -= 1
                self.ships[val-1] -= 1
                if self.ships[val-1] == 0:
                    self.shipsSunk[val-1]=True
                    print('Ship of length', val, 'sunk!')
            # print(self.player.number, self.lifeCount)
            return True
        else:
            return False

    def executeTurn(self):
        validShot = False
        while not validShot:
            shotPosition = self.player.getShot()
            validShot = self.isValidShot(shotPosition)
        self.shoot(shotPosition)


class Ship:
    def __init__(self, length):
        self.length = length

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
    testBoard = Board(8,8,'AI','AI')
    gameEnd = False
    while not gameEnd:
        # testBoard.printBoard()
        testBoard.printView()
        gameEnd = testBoard.executeTurn()
        # sleep(0.01) # Time in seconds.
