import pandas as pd


class ConfigObj:
    def __init__(self, optionsfile="../options_AAcounty.txt"):
        self.options = None

        self.readoptions(filename=optionsfile)
        self.option_headers = list(self.options.columns.values)

    def readoptions(self, filename):
        self.options = pd.read_table(filename, sep=',', header=0)
