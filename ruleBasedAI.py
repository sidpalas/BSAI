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

        #Config from file
        self.epsilon = float(config[playerType]['epsilon'])
        self.adjacent1HitValue = int(config[playerType]['adjacent1HitValue'])
        #Could parameterize the rest as well...

        self.rows = rows
        self.columns = columns
        self.boardState = np.zeros([rows, columns], dtype=int)
        self.moveQueue = []
        # self.hitQueue = deque()
        return

    def addMoveToQueue(self, position, index = -1):
        if self.isWithinBoard(position):
            if not self.hasBeenPlayed(position):
                #could evaluate the move upon insertion for speed, but the ranking could change based on the board state
                self.moveQueue.insert(index, position)
                return True
        return False

    def getBestMove(self):
        moveRankings = []
        for move in self.moveQueue:
            currentMoveRanking = self.evaluateMove(move)
            moveRankings.append(currentMoveRanking)
        print("moveRankings:", moveRankings, "moveQueue", self.moveQueue)
        maxIdx = np.argmax(moveRankings)
        return self.moveQueue.pop(maxIdx)

    def evaluateMove(self, move):
        firstTierScore = self.evaluateFirstTier(move)
        secondTierScore = self.evaluateSecondTier(move)
        bothTiersScore = self.evaluateBothTiers(move)

        #not currently being used...
        isOnEdge = self.isEdge(move)
        isInCorner = self.isCorner(move)

        score = firstTierScore + secondTierScore + bothTiersScore

        return score

    def evaluateFirstTier(self, move):
        score = 0
        for i in [0,1,2,3]:
            relativePosition = RuleAI.DIRECTION_MAPPING[i]
            evaluationPosition = [move[0] + relativePosition[0], move[1] + relativePosition[1]]
            if self.isWithinBoard(evaluationPosition):
                val = self.boardState[evaluationPosition[0], evaluationPosition[1]]
                if val == 1: #Hit
                    score += 1 #self.adjacent1HitValue
                elif val == -1: #Miss
                    score -= 1
                elif val == 0: #Unvisited
                    continue
                else:
                    raise ValueError
        return score

    def evaluateSecondTier(self, move):
        score = 0
        for i in [0,1,2,3]:
            relativePosition = RuleAI.DIRECTION_MAPPING[i]
            evaluationPosition = [move[0] + relativePosition[0]*2, move[1] + relativePosition[1]*2]
            if self.isWithinBoard(evaluationPosition):
                val = self.boardState[evaluationPosition[0], evaluationPosition[1]]
                if val == 1: #Hit
                    score += 0.5
                elif val == -1: #Miss
                    score -= 0.5
                elif val == 0: #Unvisited
                    continue
                else:
                    raise ValueError
        return score

    def evaluateBothTiers(self, move):
        score = 0
        for i in [0,1,2,3]:
            relativePosition = RuleAI.DIRECTION_MAPPING[i]
            evaluationPosition1 = [move[0] + relativePosition[0], move[1] + relativePosition[1]]
            evaluationPosition2 = [move[0] + relativePosition[0]*2, move[1] + relativePosition[1]*2]
            if self.isWithinBoard(evaluationPosition1) and self.isWithinBoard(evaluationPosition2):
                val1 = self.boardState[evaluationPosition1[0], evaluationPosition1[1]]
                val2 = self.boardState[evaluationPosition2[0], evaluationPosition2[1]]
                if min([val1,val2]) == 1: #Hit
                    score += 0.5
                elif max([val1,val2]) == -1: #Miss
                    score -= 0.5
                elif val1 == 1 and val2 == 0:
                    score += 20
                elif val1 == 0 and val2 == 1:
                    score -+ 2
                else:
                    continue
        return score

    def isEdge(self, move):
        if move[0] == 0:
            return True
        elif move[0] == self.rows-1:
            return True
        elif move[1] == 0:
            return True
        elif move[1] == self.columns-1:
            return True
        else:
            return False

    def isCorner(self, move):
        if move[0] == 0 and move[1]==0:
            return True
        elif move[0] == 0 and move[1]==self.columns-1:
            return True
        elif move[0] == self.rows-1 and move[1]==0:
            return True
        elif move[0] == self.rows-1 and move[1]==self.columns-1:
            return True
        else:
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

        # return self.moveQueue.popleft()
        return self.getBestMove()

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
                self.generateAllAdjacentMoves(prevMove, 0) #queueIndex = 0 is GREEDY, queueIndex = -1 is LAZY
        else:
            self.boardState[prevMove[0],prevMove[1]] = -1
        return
