import random


class ScenarioRandomizer:
    def __init__(self, dataframe=None):
        """  """
        self._rand_integers(dataframe)

    @staticmethod
    def _rand_integers(dataframe):
        # Generate a random integer between 1 and 1000 for each non-empty (Geo, Agency, Source, BMP) coordinate
        howmanytoreplace = (dataframe == 1).sum().sum()
        dataframe[dataframe == 1] = random.sample(range(1, 200000), howmanytoreplace)
