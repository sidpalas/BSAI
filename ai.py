from game import Player
from game import Board
from game import PlayerBoard
from game import Game


if __name__ == "__main__":
    testGame = Game(numPlayers = 1, playerTypes = ['AI'], rows=4, columns=4, showDisplay=True)
    # testGame = Game(numPlayers = 2, playerTypes = ['AI']*2, rows=4, columns=4, showDisplay=True)

    testGame.playGame()
