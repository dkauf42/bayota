from tqdm import tqdm  # Loop progress indicator module
import random


class ScenarioRandomizer:
    def __init__(self, dataframe=None):
        """  """
        self.rand_integers(dataframe)

    def rand_integers(self, dataframe):
        # Generate a random integer between 1 and 1000 for each non-empty (Geo, Agency, Source, BMP) coordinate
        howmanytoreplace = (dataframe == 1).sum().sum()
        dataframe[dataframe == 1] = random.sample(range(1, 200000), howmanytoreplace)
