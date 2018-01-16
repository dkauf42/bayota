from util.TblLoader import TblLoader
from util.OptionLoader import OptionLoader
from util.SasFilter import SasFilter
from util.BmpFilter import BmpFilter
from util.PossibilitiesMatrix import PossibilitiesMatrix


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

        # Generate a matrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.possmatrix = PossibilitiesMatrix(sasobj=self.sas, allbmps=self.tables.srcdata.allbmps_shortnames)
        print(self.possmatrix.data.head())

        # Get the list of BMPs available on the chosen load sources
        self.bmps = BmpFilter(sasobj=self.sas, sourcedataobj=self.tables.srcdata, possmatrix=self.possmatrix)
        print('<Scenario Loading Complete>')

