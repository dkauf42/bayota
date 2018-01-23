from util.TblLoader import TblLoader
from util.OptionLoader import OptionLoader
from util.PossibilitiesMatrix import PossibilitiesMatrix
from util.ScenarioRandomizer import ScenarioRandomizer
from util.InputsToCast import InputsToCast


class Scenario:
    def __init__(self, optionsfile=''):
        """A wrapper to generate and hold the metadata for a scenario

        :param optionsfile:
        """
        # Load the Source Data and Base Condition tables
        self.tables = TblLoader()

        # The scenario options (particular geographic region(s), agencies, etc.) are loaded for this scenario.
        self.options = OptionLoader(optionsfile=optionsfile, srcdataobj=self.tables.srcdata)

        # Generate a matrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.possmatrix = PossibilitiesMatrix(sourcedataobj=self.tables.srcdata,
                                              optionloaderobj=self.options,
                                              baseconditionobj=self.tables.basecond)

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        ScenarioRandomizer(self.possmatrix)

        self.possmatrix.data.to_csv('testwrite_possmatrix.csv')  # write possibilities matrix to file

        inputobj = InputsToCast(self.possmatrix)
        inputobj.matrix_to_table()

        print('<Scenario Loading Complete>')

