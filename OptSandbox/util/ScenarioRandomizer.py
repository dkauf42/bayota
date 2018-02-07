import random


class ScenarioRandomizer:
    def __init__(self, dataframe=None):
        """Generate random integers for each non-empty (Geo, Agency, Source, BMP) coordinate

        Parameters:
            dataframe (pandas dataframe):

        """
        self._rand_integers(dataframe)

    @staticmethod
    def _rand_integers(dataframe):
        howmanytoreplace = (dataframe == 1).sum().sum()
        dataframe[dataframe == 1] = random.sample(range(1, howmanytoreplace+1), howmanytoreplace)
