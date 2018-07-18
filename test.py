import json
import matplotlib.pyplot as plt
import numpy as np

from game import GameBatch

if __name__ == "__main__":

    testBatch = GameBatch(2, ['AI', 'RANDOM'], 100, 8, 8, [2,3,3,4,5], False)
    testBatch.playGames()

    # testBatch2 = GameBatch(1, ['AI'], 200, 8, 8, [2,3,3,4,5], False)
    # testBatch2.playGames()
