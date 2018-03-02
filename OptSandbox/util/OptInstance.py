from util.TblLoader import TblLoader
from tables.TblQuery import TblQuery
from util.PossibilitiesMatrices import PossibilitiesMatrices
from util.ScenarioRandomizer import ScenarioRandomizer
import pandas as pd


class OptInstance:
    def __init__(self):
        """Represent the options and subset of data necessary for conducting a particular optimization run
        """
        self.tables = None
        self.queries = None

        self.name = None
        self.description = None
        self.baseyear = None
        self.basecondname = None
        self.wastewatername = None
        self.costprofilename = None
        self.geoscalename = None
        self.geoareanames = None

        self.geographies_included = None
        # an LRSeg list for this instance (w/accompanying county, stateabbrev, in/out CBWS,
        #                                  major/minor/state basin, river

        self.agencies_included = None
        # list of agencies selected to specify free parameter groups

        self.sectors_included = None
        # list of sectors selected to specify free parameter groups

        self.possibility_matrix = pd.DataFrame()

    def __repr__(self):
        d = self.__dict__

        formattedstr = "\n***** OptInstance Details *****\n" \
                       "name:                     %s\n" \
                       "description:              %s\n" \
                       "base year:                %s\n" \
                       "base condition:           %s\n" \
                       "wastewater:               %s\n" \
                       "cost profile:             %s\n" \
                       "geographic scale:         %s\n" \
                       "geographic areas:         %s\n" \
                       "# of lrsegs:              %s\n" \
                       "agencies included:        %s\n" \
                       "sectors included:         %s\n" \
                       "possibility matrix shape: %s\n" \
                       "************************************\n" %\
                       tuple([str(i) for i in [d['name'],
                                               d['description'],
                                               d['baseyear'],
                                               d['basecondname'],
                                               d['wastewatername'],
                                               d['costprofilename'],
                                               d['geoscalename'],
                                               d['geoareanames'],
                                               d['geographies_included'].shape[0],
                                               d['agencies_included'],
                                               d['sectors_included'],
                                               d['possibility_matrix'].shape]])

        return formattedstr

    def load_tables(self):
        self.tables = TblLoader()
        self.queries = TblQuery(tables=self.tables)

    def save_metadata(self, metadata_results):
        self.name = metadata_results.name
        self.description = metadata_results.description
        self.baseyear = metadata_results.baseyear
        self.basecondname = metadata_results.basecond
        self.wastewatername = metadata_results.wastewater
        self.costprofilename = metadata_results.costprofile
        self.geoscalename = metadata_results.scale
        self.geoareanames = metadata_results.area

        self.geographies_included = None
        #self.get_geographies_included(areanames=self.geoareanames)

    def save_freeparamgrps(self, freeparamgrp_results):
        self.agencies_included = freeparamgrp_results.agencies
        self.sectors_included = freeparamgrp_results.sectors

    def set_geography(self, geotable=None):
        self.geographies_included = geotable

    def generate_possibilitymatrix(self):
        self.possibility_matrix = PossibilitiesMatrices(optinstance=self)

    def scenario_randomizer(self):
        print('OptInstance:scenario_randomizer: random integers for each (Geo, Agency, Source, BMP) coordinate')
        ScenarioRandomizer(self.possibility_matrix.ndas.matrix)
        ScenarioRandomizer(self.possibility_matrix.anim.matrix)
        ScenarioRandomizer(self.possibility_matrix.manu.matrix)

        self.possibility_matrix.ndas.matrix.to_csv('./output/testwrite_Scenario_possmatrix_ndas.csv')  # write possibilities matrix to file
        self.possibility_matrix.anim.matrix.to_csv('./output/testwrite_Scenario_possmatrix_anim.csv')  # write possibilities matrix to file
        self.possibility_matrix.manu.matrix.to_csv('./output/testwrite_Scenario_possmatrix_manu.csv')  # write possibilities matrix to file
