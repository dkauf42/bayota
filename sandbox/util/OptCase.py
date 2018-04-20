import pandas as pd
import os
from sandbox.util.TblJeeves import TblJeeves
from sandbox.util.ScenarioMaker import ScenarioMaker
from sandbox.util.PopulationMaker import PopulationMaker
from sandbox.util.Examples import Examples
from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


class OptCase:
    def __init__(self):
        """Represent the options and subset of data necessary for conducting a particular optimization run
        """
        self.logtostdout = False
        self.successful_creation_log = False

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

        # Intermediary tables for Decision Variable Space
        self.lrseg_agency_table = None
        self.source_lrseg_agency_table = None
        self.source_county_agency_table = None
        # For land bmps (no bounds yet)
        self.land_slabidtable = None
        self.land_slabnametable = None
        # For animal bmps (no bounds yet)
        self.animal_scabidtable = None
        self.animal_scabnametable = None
        # For manure bmps (no bounds yet)
        self.manure_sftabidtable = None
        self.manure_sftabnametable = None

        # Decision space vectors with hard bounds
        self.land_decisionspace = None
        self.animal_decisionspace = None
        self.manure_decisionspace = None

        # Scenarios
        self.scenarios_land = []
        self.scenarios_animal = []
        self.scenarios_manure = []

    def __repr__(self):
        """ Custom 'print' that displays the metadata defined for this OptCase.
        """
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
                                               d['sectorids']
                                               ]
                              ])

        return formattedstr

    def load_example(self, name=''):
        """ load pre-defined example metadata options for testing purposes

        Parameters:
            name (str):  this is the name of the example to load.

        """
        ex = Examples(name)

        self.name = ex.name
        self.description = ex.description
        self.baseyear = ex.baseyear
        self.basecondname = ex.basecondname
        self.wastewatername = ex.wastewatername
        self.costprofilename = ex.costprofilename
        self.geoscalename = ex.geoscalename
        self.geoareanames = ex.geoareanames

    def custom_scenario(self, scale='', areanames=''):
        ex = Examples('basenogeography')

        self.name = ex.name
        self.description = ex.description
        self.baseyear = ex.baseyear
        self.basecondname = ex.basecondname
        self.wastewatername = ex.wastewatername
        self.costprofilename = ex.costprofilename

        self.geoscalename = scale
        self.geoareanames = areanames

    def load_tables(self):
        self.queries = TblJeeves()

    def set_geography(self, geotable=None):
        self.lrsegids = geotable

    # Decision space generation methods
    def proceed_from_geography_to_decision_space(self):
        """ Generate a decision space from just a geography (scale + area names)

        Note:
            This will include all agencies, all loadsources, and all bmps.
        """
        # Metadata to BMPs
        self.populate_geography_from_scale_and_areas()
        self.populate_agencies_from_geography()
        self.populate_sectors()
        self.populate_loadsources()
        self.populate_bmps()
        # QA/QC tables by removing unnecessary BMPs
        self.qaqc_land_decisionspace()
        self.qaqc_animal_decisionspace()
        self.qaqc_manure_decisionspace()
        # Replicate the slab, scab, and sftab tables with hard upper/lower bounds where possible.
        self.populate_hardbounds()

    def proceed_from_geoagencysectorids_to_decision_space(self):
        """ Generate a decision space from pre-defined geography (scale + area names), agency, and sector ids.
        """
        self.populate_lrsegagencytable_from_geoagencysectorids()
        # Metadata to BMPs
        self.populate_loadsources()
        self.populate_bmps()
        # QA/QC tables by removing unnecessary BMPs
        self.qaqc_land_decisionspace()
        self.qaqc_animal_decisionspace()
        self.qaqc_manure_decisionspace()
        # Replicate the slab, scab, and sftab tables with hard upper/lower bounds where possible.
        self.populate_hardbounds()

    def populate_geography_from_scale_and_areas(self):
        self.lrsegids = self.queries.lrsegids_from_geoscale_with_names(scale=self.geoscalename,
                                                                       areanames=self.geoareanames)
        self.countyids = self.queries.countyids_from_lrsegids(lrsegids=self.lrsegids)

    def populate_agencies_from_geography(self):
        """ make la_table from lrsegids alone """
        self.lrseg_agency_table = self.queries.agencylrsegidtable_from_lrsegids(lrsegids=self.lrsegids)
        self.agencyids = self.lrseg_agency_table.loc[:, ['agencyid']]

    def populate_sectors(self):
        self.sectorids = self.queries.all_sectorids()

    def populate_lrsegagencytable_from_geoagencysectorids(self):
        """ make la_table when agencyids have already been populated """
        all_lrseg_agencyids_table = self.queries.agencylrsegidtable_from_lrsegids(lrsegids=self.lrsegids)

        columnmask = ['lrsegid', 'agencyid']
        self.lrseg_agency_table = all_lrseg_agencyids_table.loc[:, columnmask].merge(self.agencyids, how='inner')

    def populate_loadsources(self):
        self.source_lrseg_agency_table = self.\
            queries.sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=self.lrseg_agency_table,
                                                                       sectorids=self.sectorids)

        self.source_county_agency_table = self.\
            queries.sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=self.
                                                                            source_lrseg_agency_table)

    def populate_bmps(self):
        """ Append the IDs for land, animal, and manure BMPs to the decision space tables
        """
        """ LAND BMPs """
        # get IDs
        self.land_slabidtable = self.queries.\
            land_slabidtable_from_SourceLrsegAgencyIDtable(SourceLrsegAgencyIDtable=self.
                                                           source_lrseg_agency_table)
        # Translate to names
        self.land_slabnametable = self.queries.translate_slabidtable_to_slabnametable(self.land_slabidtable)

        """ ANIMAL BMPs """
        # get IDs
        self.animal_scabidtable = \
            self.queries.animal_scabidtable_from_SourceCountyAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                                           source_county_agency_table,
                                                                           baseconditionid=self.baseconditionid)
        # Translate to names
        self.animal_scabnametable = self.queries.translate_scabidtable_to_scabnametable(self.animal_scabidtable)

        """ MANURE BMPs """
        # get IDs
        self.manure_sftabidtable = \
            self.queries.manure_sftabidtable_from_SourceFromToAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                                            source_county_agency_table,
                                                                            baseconditionid=self.baseconditionid)
        # Translate to names
        self.manure_sftabnametable = self.queries.translate_sftabidtable_to_sftabnametable(self.manure_sftabidtable)

    def populate_hardbounds(self):
        # TODO: code this
        self.land_decisionspace = self.queries.\
            appendBounds_to_land_slabidtable(slabidtable=self.land_slabidtable)
        self.animal_decisionspace = self.queries.\
            appendBounds_to_animal_scabidtable(scabidtable=self.animal_scabidtable)
        self.manure_decisionspace = self.queries.\
            appendBounds_to_manure_sftabidtable(sftabidtable=self.manure_sftabidtable)

    # QA/QC the decision space
    def qaqc_land_decisionspace(self):
        """ Remove BMPs that the optimization engine should not modify

        The following BMPs are removed from the decision space:
        - Urban Stream Restoration Protocol
        - Non-Urban Stream Restoration Protocol
        - Stormwater Performance Standards (RR [runoff reduction] and ST [stormwater treatment])
        - Land policy BMPs

        """
        if self.logtostdout:
            print('OptCase.qaqc_land_decisionspace(): QA/QCing...')
            print('Decision Space Table size: %s' % (self.land_slabidtable.shape, ))

        origrowcnt, origcolcnt = self.land_slabidtable.shape

        removaltotal = 0

        # Remove "Urban Stream Restoration Protocol" BMP
        bmpnametoremove = 'UrbStrmRestPro'
        bmpid = self.queries.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if self.logtostdout:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove "Non-Urban Stream Restoration Protocol" BMP
        bmpnametoremove = 'NonUrbStrmRestPro'
        bmpid = self.queries.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if self.logtostdout:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove "Stormwater Performance Standard" BMPs (RR [runoff reduction] and ST [stormwater treatment])
        bmpnametoremove = 'RR'
        bmpid = self.queries.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if self.logtostdout:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        bmpnametoremove = 'ST'
        bmpid = self.queries.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if self.logtostdout:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove Policy BMPs
        bmpids = self.queries.bmpids_from_categoryids(categoryids=[4])
        mask = pd.Series(self.land_slabidtable['bmpid'].isin(bmpids.bmpid.tolist()))
        # TODO: replace the above '4' with a call that gets the number from a string such as 'Land Policy BMPs'
        self.land_slabidtable = self.land_slabidtable[~self.land_slabidtable['bmpid'].isin(bmpids.bmpid.tolist())]
        removaltotal += mask.sum()
        if self.logtostdout:
            print('removing %d for %s' % (mask.sum(), 'Land Policy BMPs'))

        newrowcnt, newcolcnt = self.land_slabidtable.shape
        if self.logtostdout:
            print('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                  (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def qaqc_animal_decisionspace(self):
        pass

    def qaqc_manure_decisionspace(self):
        pass

    # hooks for graphical interface get/put
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

    def save_freeparamgrps(self, freeparamgrp_results):
        self.agencyids = self.queries.agencyids_from(agencycodes=freeparamgrp_results.agencies)
        self.sectorids = self.queries.sectorids_from(sectornames=freeparamgrp_results.sectors)

    # Generating scenario(s) from the decision space
    def generate_scenario(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        # TODO: code this (randomization for each variable, and then writing to file)
        scenario = ScenarioMaker()
        scenario.initialize_from_decisionspace(land=self.land_decisionspace,
                                               animal=self.animal_decisionspace,
                                               manure=self.manure_decisionspace)

        if scenariotype == 'random':
            scenario.randomize_betweenbounds()
        else:
            scenario.randomize_betweenbounds()

        # translate the columns that are ids to names
        self.scenarios_land.append(self.queries.translate_slabidtable_to_slabnametable(slabidtable=scenario.land))
        self.scenarios_animal.append(self.queries.translate_scabidtable_to_scabnametable(scabidtable=scenario.animal))
        self.scenarios_manure.append(self.queries.translate_sftabidtable_to_sftabnametable(sftabidtable=scenario.manure))

        # Scenario is written to file.
        self.scenarios_land[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_land.csv'))
        self.scenarios_animal[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_animal.csv'))
        self.scenarios_manure[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_manure.csv'))

    def generate_multiple_scenarios(self, scenariotype=''):
        """ Create a scenario (as CAST-input-tables in .csv format), and write them to file.

        The scenario is created by randomly generating numbers for each variable in the decision space.

        """
        population = PopulationMaker()
        population.initialize_from_decisionspace(land=self.land_decisionspace,
                                                 animal=self.animal_decisionspace,
                                                 manure=self.manure_decisionspace)

        if scenariotype == 'hypercube':
            population.generate_latinhypercube()
        else:
            population.generate_latinhypercube()

        # columns that are ids are translated to names, and scenarios are written to file.
        i = 0
        for df in population.scenarios_land:
            self.scenarios_land.append(self.queries.translate_slabidtable_to_slabnametable(slabidtable=df))
            self.scenarios_land[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_land_%d.txt' % i),
                                           sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in population.scenarios_animal:
            self.scenarios_animal.append(self.queries.translate_scabidtable_to_scabnametable(scabidtable=df))
            self.scenarios_animal[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_animal_%d.txt' % i),
                                             sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1

        i = 0
        for df in population.scenarios_manure:
            self.scenarios_manure.append(self.queries.translate_sftabidtable_to_sftabnametable(sftabidtable=df))
            self.scenarios_manure[-1].to_csv(os.path.join(writedir, 'testwrite_CASTscenario_manure_%d.txt' % i),
                                             sep='\t', header=True, index=False, line_terminator='\r\n')
            i += 1
