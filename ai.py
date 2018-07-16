from game import Player
from game import Board
from game import PlayerBoard


def playGame(numPlayers, playerTypes, rows, columns, showDisplay = True):
    if numPlayers == 1:
        trainingPlayer = Player(1, playerTypes[0])
        trainingBoard = PlayerBoard(rows, columns, trainingPlayer, showDisplay)
        gameEnd = False
        while not gameEnd:
            gameEnd = trainingBoard.executeTurn()
            # sleep(0.01)
        return
    elif numPlayers == 2:
        # 2 players (head to head):
        testBoard = Board(rows, columns, playerTypes[0], playerTypes[1], showDisplay)
        gameEnd = False
        i = 0
        while not gameEnd:
            gameEnd = testBoard.executeTurn()
            # sleep(0.01)
        return
    else:
        raise ValueError


if __name__ == "__main__":
    # playGame(numPlayers = 1, playerTypes = ['AI'], rows=4, columns=4, showDisplay=True)
    playGame(numPlayers = 2, playerTypes = ['AI']*2, rows=4, columns=4, showDisplay=True)
