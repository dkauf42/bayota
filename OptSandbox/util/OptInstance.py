import pandas as pd
from tables.TblQuery import TblQuery
from util.ScenarioRandomizer import ScenarioRandomizer
from tables.MatrixSand import MatrixSand
from tables.MatrixAnimal import MatrixAnimal
from tables.MatrixManure import MatrixManure


class OptInstance:
    def __init__(self):
        """Represent the options and subset of data necessary for conducting a particular optimization run
        """
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

        self.pmatrices = {'animal': None,
                          'manure': None,
                          'ndas': None}
        # Parameter/possibility matrices for each large bmp type

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
                                               d['pmatrices']]])

        return formattedstr

    def load_tables(self):
        self.queries = TblQuery()

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
            Ya'ad means target (i.e. BMP application target)
        """

        # An empty emptyparametermatrix is created for each Segment-Agency-Type table.
        self.pmatrices['ndas'] = MatrixSand(name='ndas', geographies=self.geographies_included,
                                            agencies=self.agencies_included, queries=self.queries)
        self.pmatrices['animal'] = MatrixAnimal(name='anim', geographies=self.geographies_included,
                                                queries=self.queries)
        self.pmatrices['manure'] = MatrixManure(name='manu', geographies=self.geographies_included,
                                                queries=self.queries)

    def mark_eligibility(self):
        # A numpy array is created that contains all load sources in this scenario.
        self.load_sources_included = pd.concat([self.pmatrices['ndas'].
                                               yaad_table.index.get_level_values('LoadSource').to_series(),
                                                self.pmatrices['animal'].
                                               yaad_table.index.get_level_values('LoadSource').to_series(),
                                                self.pmatrices['manure'].
                                               yaad_table.index.get_level_values('LoadSource').to_series()],
                                               ignore_index=True).unique()

        # A dictionary is generated with <keys:loadsource>, <values:eligible BMPs>.
        bmpdict = self.queries.source.get_dict_of_bmps_by_loadsource_keys(load_sources=self.load_sources_included)

        # NonNaN markers are generated for eligible (Geo, Agency, Source, BMP) coordinates in the emptyparametermatrix
        self.pmatrices['ndas'].mark_eligible_coordinates(bmpdict=bmpdict)
        self.pmatrices['animal'].mark_eligible_coordinates(bmpdict=bmpdict)
        self.pmatrices['manure'].mark_eligible_coordinates(bmpdict=bmpdict)

    def generate_boundsmatrices(self):
        # Associate a hard lower and upper bound with each marker coordinate in the emptyparametermatrix
        self.pmatrices['animal'].identifyhardupperbounds()
        self.pmatrices['manure'].identifyhardupperbounds()
        self.pmatrices['ndas'].identifyhardupperbounds()

    def scenario_randomizer(self):
        #ScenarioRandomizer(self.pmatrices['ndas'].eligibleparametermatrix)
        #ScenarioRandomizer(self.pmatrices['animal'].eligibleparametermatrix)
        #ScenarioRandomizer(self.pmatrices['manure'].eligibleparametermatrix)

        # write possibility/parameter matrices to file
        self.pmatrices['ndas'].eligibleparametermatrix.to_csv('./output/testwrite_Scenario_possmatrix_ndas.csv')
        self.pmatrices['animal'].eligibleparametermatrix.to_csv('./output/testwrite_Scenario_possmatrix_anim.csv')
        self.pmatrices['manure'].eligibleparametermatrix.to_csv('./output/testwrite_Scenario_possmatrix_manu.csv')
