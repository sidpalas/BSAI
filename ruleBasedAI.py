import configparser
from collections import deque
from random import randint
import numpy as np

class RuleAI:

    DIRECTION_MAPPING = {0:[-1,0],1:[0,1],2:[1,0],3:[0,-1]}

    def __init__(self, rows, columns, playerType):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.playerType = playerType
        self.epsilon = int(config[playerType]['epsilon'])
        self.rows = rows
        self.columns = columns
        self.boardState = np.zeros([rows, columns], dtype=int)
        self.moveQueue = deque()
        # self.hitQueue = deque()
        return

    def addMoveToQueue(self, position, index = -1):
        if self.isWithinBoard(position):
            if not self.hasBeenPlayed(position):
                print(index)
                self.moveQueue.insert(index, position)
                return True
        return False

    def hasBeenPlayed(self, position):
        if self.boardState[position[0], position[1]] != 0:
            return True
        else:
            return False

    def isWithinBoard(self, position):
        if position[0] not in range(self.rows) or position[1] not in range(self.columns):
            return False
        else:
            return True

    def isQueueEmpty(self):
        return len(self.moveQueue) == 0

    def getNextMove(self):
        while self.isQueueEmpty():
            #if no moves are left, generate random moves and add them to the queue
            self.generateRandomMove()
        #moves are sanitized (checked for validity and prior use) before adding to queue
        #within self.addMoveToQueue()
        return self.moveQueue.popleft()

    def generateRandomMove(self):
        return self.addMoveToQueue([randint(0,self.rows-1),randint(0,self.columns-1), 0], index = 0)

    def generateAdjacentMoves(self, position, directionIndices, queueIndex):
        for directionIndex in directionIndices:
            relativePosition = RuleAI.DIRECTION_MAPPING[directionIndex]
            newRow = position[0] + relativePosition[0]
            newColumn = position[1] + relativePosition[1]
            move = [newRow, newColumn, directionIndex]
            self.addMoveToQueue(move, queueIndex) #queueIndex will be configurable

    def generateAllAdjacentMoves(self, position, queueIndex):
        self.generateAdjacentMoves(position, [0,1,2,3], queueIndex)

    def generateVerticalMoves(self, position, queueIndex):
        self.generateAdjacentMoves(position, [0,2], queueIndex)

    def generateHorizontalMoves(self, position, queueIndex):
        self.generateAdjacentMoves(position, [1,3], queueIndex)

    def generateUpMove(self, position, queueIndex):
        self.generateAdjacentMoves(position, [0], queueIndex)

    def generateDownMove(self, position, queueIndex):
        self.generateAdjacentMoves(position, [2], queueIndex)

    def generateRightMove(self, position, queueIndex):
        self.generateAdjacentMoves(position, [1], queueIndex)

    def generateLeftMove(self, position, queueIndex):
        self.generateAdjacentMoves(position, [3], queueIndex)

    def generateNewMoves(self):
        return

    def executeTurn(self):
        return self.getNextMove()

    def postExecution(self,prevMove, isHit):
        # Need to keep track of last move, direction of exploration, to determine which branch to go down...
        # moveDirection
        # isHit?
        if isHit:
            self.boardState[prevMove[0],prevMove[1]] = 1
            if np.random.rand() <= self.epsilon:
                while not self.generateRandomMove():
                    continue #keep trying to add random moves until one succeeds
            else:
                self.generateAllAdjacentMoves(prevMove, 0) #queueIndex = 0 is GREEDY
        else:
            self.boardState[prevMove[0],prevMove[1]] = -1
        return