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

        # Options are used to query the BaseCondition data and get the Load Sources for each segment-agency pair
        self.sas = SasFilter(optionloaderobj=self.options, baseconditionobj=self.tables.basecond)

        # Generate a matrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.possmatrix = PossibilitiesMatrix(sasobj=self.sas, sourcedataobj=self.tables.srcdata)

        # Get the list of BMPs available on the chosen load sources
        self.bmpfilter = BmpFilter(sasobj=self.sas, sourcedataobj=self.tables.srcdata, possmatrix=self.possmatrix)

        self.possmatrix.data.to_csv('testwrite_possmatrix.csv')  # write possibilities matrix to file


        print('<Scenario Loading Complete>')

