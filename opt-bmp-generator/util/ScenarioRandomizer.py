from tqdm import tqdm  # Loop progress indicator module
import random


class ScenarioRandomizer:
    def __init__(self, possmatrix=None):
        """
        """
        self.possmatrix = possmatrix

        self.rand_integers()

    def rand_integers(self):
        # Generate a random integer between 1 and 1000 for each non-zero SAS-B combination
        n = len(self.possmatrix.data.index)
        print('Generating random integers for each SAS-B combination')
        for index, row in tqdm(self.possmatrix.data.iterrows(), total=n):
            numones = (row == 1).sum()
            row[row == 1] = random.sample(range(1, 1000), numones)
