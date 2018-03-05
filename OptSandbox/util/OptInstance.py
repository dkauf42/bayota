import pandas as pd
from util.TblLoader import TblLoader
from tables.TblQuery import TblQuery
from util.ScenarioRandomizer import ScenarioRandomizer
from tables.MatrixSand import MatrixSand
from tables.MatrixAnimal import MatrixAnimal
from tables.MatrixManure import MatrixManure


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

        self.load_sources_included = None
        # list of load sources selected included in the geography-agencies

        self.sand = None
        self.animal = None
        self.manure = None

        self.parameter_matrices = {'animal': None,
                                   'manure': None,
                                   'ndas': None}
        # list of load sources selected included in the geography-agencies
        # Three of sectors selected to specify free parameter groups

        self.bounds_matrices = {'animal': pd.DataFrame(),
                                'manure': pd.DataFrame(),
                                'ndas': pd.DataFrame()}

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
                       "parameter matrices: %s\n" \
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
                                               d['parameter_matrices']]])

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

    def generate_emptyparametermatrices(self):
        """An empty emptyparametermatrix is created for each Segment-Agency-Type table.

        The Specs:
            Land: rows=seg-agency-sources X columns=BMPs.
            Animal: rows=FIPS-animal-sources X columns=BMPs
            Manure: rows=FIPSto-FIPSfrom-animal-sources X columns=BMPs

        Note:
            Ya'ad means target
        """

        # Load source tables are generated.
        yaadtables = self.queries.loadsources. \
            get_tables_of_load_sources_and_their_units_and_amounts_by_geoagencies(geographies=self.geographies_included,
                                                                                  agencies=self.agencies_included)
        # A numpy array is saved to this optinstance that contains all load sources in this scenario.
        self.load_sources_included = pd.concat([yaadtables.ndas.index.get_level_values('LoadSource').to_series(),
                                                yaadtables.animal.index.get_level_values('LoadSource').to_series(),
                                                yaadtables.manure.index.get_level_values('LoadSource').to_series()],
                                               ignore_index=True).unique()

        # An empty emptyparametermatrix is created for each Segment-Agency-Type table.
        self.parameter_matrices['ndas'] = MatrixSand(name='ndas', row_indices=yaadtables.ndas.index,
                                                     column_names=self.tables.srcdata.allbmps_shortnames)
        self.parameter_matrices['animal'] = MatrixAnimal(name='anim', row_indices=yaadtables.animal.index,
                                                         column_names=self.tables.srcdata.allbmps_shortnames)
        self.parameter_matrices['manure'] = MatrixManure(name='manu', row_indices=yaadtables.manure.index,
                                                         column_names=self.tables.srcdata.allbmps_shortnames)

    def mark_eligibility(self):
        # A dictionary is generated with <keys:loadsource>, <values:eligible BMPs>.
        bmpdict = self.queries.source.get_dict_of_bmps_by_loadsource_keys(load_sources=self.load_sources_included)

        # NonNaN markers are generated for eligible (Geo, Agency, Source, BMP) coordinates in the possibilities emptyparametermatrix
        self.parameter_matrices['ndas'].mark_eligible_coordinates(bmpdict=bmpdict)
        self.parameter_matrices['animal'].mark_eligible_coordinates(bmpdict=bmpdict)
        self.parameter_matrices['manure'].mark_eligible_coordinates(bmpdict=bmpdict)

    def generate_boundsmatrices(self):
        # TODO: upper_bounds = self._identifyhardupperbounds(sat)
        # Associate a hard lower and upper bound with each marker coordinate in the emptyparametermatrix
        pass

    def scenario_randomizer(self):
        print('OptInstance:scenario_randomizer: random integers for each (Geo, Agency, Source, BMP) coordinate')
        ScenarioRandomizer(self.parameter_matrices['ndas'].eligibleparametermatrix)
        ScenarioRandomizer(self.parameter_matrices['animal'].eligibleparametermatrix)
        ScenarioRandomizer(self.parameter_matrices['manure'].eligibleparametermatrix)

        self.parameter_matrices['ndas'].eligibleparametermatrix.to_csv('./output/testwrite_Scenario_possmatrix_ndas.csv')  # write possibilities emptyparametermatrix to file
        self.parameter_matrices['animal'].eligibleparametermatrix.to_csv('./output/testwrite_Scenario_possmatrix_anim.csv')  # write possibilities emptyparametermatrix to file
        self.parameter_matrices['manure'].eligibleparametermatrix.to_csv('./output/testwrite_Scenario_possmatrix_manu.csv')  # write possibilities emptyparametermatrix to file
