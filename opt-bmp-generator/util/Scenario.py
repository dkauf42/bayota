from util.TblLoader import TblLoader
from util.OptionLoader import OptionLoader
from util.IncludeSpec import IncludeSpec
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

        # Geographic region is extracted from SourceData, so the list of lrsegs (etc.) can be used as a boolean mask
        self.includespec = IncludeSpec(optionloaderobj=self.options, tables=self.tables)

        # Generate a matrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.possmatrix = PossibilitiesMatrix(tables=self.tables, includespec=self.includespec)

        # Populate the Possibilities Matrix with a random assortment of numbers for each ST-B combination
        print('>> Generating random integers for each (Geo, Agency, Source, BMP) coordinate')
        ScenarioRandomizer(self.possmatrix.ndas)
        ScenarioRandomizer(self.possmatrix.anim)
        ScenarioRandomizer(self.possmatrix.manu)

        self.possmatrix.ndas.to_csv('testwrite_possmatrix_ndas.csv')  # write possibilities matrix to file
        self.possmatrix.anim.to_csv('testwrite_possmatrix_anim.csv')  # write possibilities matrix to file
        self.possmatrix.manu.to_csv('testwrite_possmatrix_manu.csv')  # write possibilities matrix to file

        inputobj = InputsToCast(self.possmatrix)
        inputobj.matrix_to_table()

        print('<Scenario Loading Complete>')

