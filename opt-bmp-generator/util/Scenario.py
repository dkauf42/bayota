from util.TblLoader import TblLoader
from util.OptionLoader import OptionLoader
from util.SasFilter import SasFilter
from util.BmpFilter import BmpFilter


class Scenario:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        :param optionsfile:
        """
        # Load the Source Data and Base Condition tables
        self.tables = TblLoader()

        # The scenario options (particular geographic region(s), agencies, etc.) are loaded for this scenario.
        self.options = OptionLoader(optionsfile=optionsfile, srcdataobj=self.tables.srcdata)

        # Options are used to query the BaseCondition data and filter only Load Sources with the chosen characteristics
        self.sas = SasFilter(optionloaderobj=self.options, baseconditionobj=self.tables.basecond)

        # Get the list of BMPs available on the chosen load sources
        self.bmps = BmpFilter(sasobj=self.sas, sourcedataobj=self.tables.srcdata)
        print('<Scenario Loading Complete>')

