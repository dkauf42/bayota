import pandas as pd


class ConfigObj:
    """Loads an 'options' file that represents the user choices for a particular scenario

    Parameters
    ----------
    optionsfile : `str`
        file path of the 'options' csv file for the user scenario

    Notes
    -----
    The options file should have the following columns:
        - BaseCondition,LandRiverSegment,CountyName,StateAbbreviation,StateBasin,OutOfCBWS,AgencyCode
    Any blank options should be specified by a '-'

    """
    def __init__(self, optionsfile="../options_AAcounty.txt"):
        self.options = None

        self.readoptions(filename=optionsfile)
        self.option_headers = list(self.options.columns.values)

    def readoptions(self, filename):
        self.options = pd.read_table(filename, sep=',', header=0)
