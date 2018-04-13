import pandas as pd
import os
from sandbox.tables.TblJeeves import TblJeeves
from sandbox.matrices.MatrixSand import MatrixSand
from sandbox.matrices.MatrixAnimal import MatrixAnimal
from sandbox.matrices.MatrixManure import MatrixManure
from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


class OptCase:
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

        # Individual Components for metadata
        self.baseconditionid = pd.DataFrame(data=[1], columns=['baseconditionid'])
        # TODO: use real baseconditionid instead of this^ temporary placeholder

        # Individual Components for decision space
        self.lrsegids = None  # an LRSeg list for this instance
        self.countyids = None  # a County list for this instance
        self.agencyids = None  # list of agencies selected to specify free parameter groups
        self.sectorids = None  # list of sectors selected to specify free parameter groups
        self.loadsourceids = None  # list of load sources selected included in the lrsegids-agencies

        # Tables for Decision Variable Space
        self.lrseg_agency_table = None
        self.source_lrseg_agency_table = None
        self.source_county_agency_table = None
        # Decision Vector - Land
        self.land_slabidtable = None
        self.land_slabnametable = None
        # Decision Vector - Animal
        self.animal_scabidtable = None
        self.animal_scabnametable = None
        # Decision Vector - Manure
        self.manure_sftabidtable = None
        self.manure_sftabnametable = None

        # self.pmatrices = dict.fromkeys(['animal', 'manure', 'ndas'])
        # # self.pmatrices = {'animal': None,
        # #                  'manure': None,
        # #                  'ndas': None}
        #
        # # Parameter/possibility matrices for each large bmp type
        #
        # self.bounds_matrices = {'animal': pd.DataFrame(),
        #                         'manure': pd.DataFrame(),
        #                         'ndas': pd.DataFrame()}

    def __repr__(self):
        d = self.__dict__

        formattedstr = "\n***** OptCase Details *****\n" \
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
                                               d['lrsegids'].shape[0],
                                               d['agencyids'],
                                               d['sectorids'],
                                               d['pmatrices']]])

        return formattedstr

    def load_tables(self):
        self.queries = TblJeeves()

    def set_geography(self, geotable=None):
        self.lrsegids = geotable

    def populate_geography_from_scale_and_areas(self):
        self.lrsegids = self.queries.lrsegids_from_geoscale_with_names(scale=self.geoscalename,
                                                                       areanames=self.geoareanames)
        self.countyids = self.queries.countyids_from_lrsegids(lrsegids=self.lrsegids)

    def populate_agencies_from_geography(self):
        self.agencyids = self.queries.agencyids_from_lrsegids(lrsegids=self.lrsegids)
        self.lrseg_agency_table = self.queries.agencyidPlusLRsegs_from_lrsegids(lrsegids=self.lrsegids)

    def populate_sectors(self):
        self.sectorids = self.queries.all_sectorids()

    def populate_loadsources(self):
        self.source_lrseg_agency_table = self.\
            queries.sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=self.lrseg_agency_table,
                                                                       sectorids=self.sectorids)

        self.source_county_agency_table = self.\
            queries.sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=self.
                                                                            source_lrseg_agency_table)

        # self.source_lrseg_agency_table.to_csv(os.path.join(writedir, 'testwrite_lalidtable.csv'))
        # self.source_county_agency_table.to_csv(os.path.join(writedir, 'testwrite_lacidtable.csv'))

    def populate_land_bmps(self):
        # Get BMP IDs
        self.land_slabidtable = self.queries.\
            land_slabidtable_from_SourceLrsegAgencyIDtable(SourceLrsegAgencyIDtable=self.
                                                           source_lrseg_agency_table)
        # Translate BMP IDs to Names
        self.land_slabnametable = self.queries.\
            translate_slabidtable_to_slabnametable(self.land_slabidtable)
        # Write Table to File
        self.land_slabidtable.\
            to_csv(os.path.join(writedir, 'testwrite_scenariolandbmpswithids.csv'))
        self.land_slabnametable.\
            to_csv(os.path.join(writedir, 'testwrite_scenariolandbmpswithnames.csv'))

    def populate_animal_bmps(self):
        # Get BMP IDs
        self.animal_scabidtable = \
            self.queries.animal_scabidtable_from_SourceCountyAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                                           source_county_agency_table,
                                                                           baseconditionid=self.baseconditionid)
        # Translate BMP IDs to Names
        self.animal_scabnametable = \
            self.queries.translate_scabidtable_to_scabnametable(self.animal_scabidtable)
        # Write Table to File
        self.animal_scabidtable.\
            to_csv(os.path.join(writedir, 'testwrite_scenarioanimalbmpswithids.csv'))
        self.animal_scabnametable.\
            to_csv(os.path.join(writedir, 'testwrite_scenarioanimalbmpswithnames.csv'))

    def populate_manure_bmps(self):
        # Get BMP IDs
        self.manure_sftabidtable = \
            self.queries.manure_sftabidtable_from_SourceFromToAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                                            source_county_agency_table,
                                                                            baseconditionid=self.baseconditionid)
        # Translate BMP IDs to Names
        self.manure_sftabnametable = \
            self.queries.translate_sftabidtable_to_sftabnametable(self.manure_sftabidtable)
        # Write Table to File
        self.manure_sftabidtable.\
            to_csv(os.path.join(writedir, 'testwrite_scenariomanurebmpswithids.csv'))
        self.manure_sftabnametable.\
            to_csv(os.path.join(writedir, 'testwrite_scenariomanurebmpswithnames.csv'))

    def save_metadata(self, metadata_results):
        self.name = metadata_results.name
        self.description = metadata_results.description
        self.baseyear = metadata_results.baseyear
        self.basecondname = metadata_results.basecond
        self.wastewatername = metadata_results.wastewater
        self.costprofilename = metadata_results.costprofile
        self.geoscalename = metadata_results.scale
        self.geoareanames = metadata_results.area  # For Counties, this is in the form of "[County], [StateAbbeviation]"

        self.lrsegids = None
        #self.get_geographies_included(areanames=self.geoareanames)

    def save_freeparamgrps(self, freeparamgrp_results):
        self.agencyids = freeparamgrp_results.agencies
        self.sectorids = freeparamgrp_results.sectors

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
        self.pmatrices['ndas'] = MatrixSand(name='ndas',
                                            geographies=self.lrsegids,
                                            agencies=self.agencyids,
                                            sectors=self.sectorids,
                                            queries=self.queries)
        self.pmatrices['animal'] = MatrixAnimal(name='anim',
                                                geographies=self.lrsegids,
                                                queries=self.queries)
        self.pmatrices['manure'] = MatrixManure(name='manu',
                                                geographies=self.lrsegids,
                                                queries=self.queries)

    def mark_eligibility(self):
        # A numpy array is created that contains all load sources in this scenario.
        self.loadsourceids = pd.concat([self.pmatrices['ndas'].
                                       yaad_table.index.get_level_values('LoadSource').to_series(),
                                        self.pmatrices['animal'].
                                       yaad_table.index.get_level_values('LoadSource').to_series(),
                                        self.pmatrices['manure'].
                                       yaad_table.index.get_level_values('LoadSource').to_series()],
                                       ignore_index=True).unique()

        # A dictionary is generated with <keys:loadsource>, <values:eligible BMPs>.
        bmpdict = self.queries.source.get_dict_of_bmps_by_loadsource_keys(load_sources=self.loadsourceids)

        # NonNaN markers are generated for eligible (Geo, Agency, Source, BMP) coordinates in the emptyparametermatrix
        self.pmatrices['ndas'].mark_eligible_coordinates(bmpdict=bmpdict)
        self.pmatrices['animal'].mark_eligible_coordinates(bmpdict=bmpdict)
        self.pmatrices['manure'].mark_eligible_coordinates(bmpdict=bmpdict)

    def generate_boundsmatrices(self):
        # Associate a hard lower and upper bound with each marker coordinate in the emptyparametermatrix
        self.pmatrices['ndas'].identifyhardupperbounds()
        self.pmatrices['animal'].identifyhardupperbounds()
        self.pmatrices['manure'].identifyhardupperbounds()

        self.pmatrices['ndas'].identifyhardlowerbounds()
        self.pmatrices['animal'].identifyhardlowerbounds()
        self.pmatrices['manure'].identifyhardlowerbounds()

    def scenario_randomizer(self):
        self.pmatrices['ndas'].randomize_belowhub()
        self.pmatrices['animal'].randomize_belowhub()
        self.pmatrices['manure'].randomize_belowhub()
        #ScenarioRandomizer(self.pmatrices['ndas'].eligibleparametermatrix)
        #ScenarioRandomizer(self.pmatrices['animal'].eligibleparametermatrix)
        #ScenarioRandomizer(self.pmatrices['manure'].eligibleparametermatrix)

        # write possibility/parameter matrices to file
        self.pmatrices['ndas'].eligibleparametermatrix.\
            to_csv(os.path.join(writedir, 'testwrite_Scenario_possmatrix_ndas.csv'))
        self.pmatrices['animal'].eligibleparametermatrix.\
            to_csv(os.path.join(writedir, 'testwrite_Scenario_possmatrix_anim.csv'))
        self.pmatrices['manure'].eligibleparametermatrix.\
            to_csv(os.path.join(writedir, 'testwrite_Scenario_possmatrix_manu.csv'))
