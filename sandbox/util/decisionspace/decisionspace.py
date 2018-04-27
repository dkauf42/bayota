import collections
import pandas as pd

from sandbox.util.jeeves import Jeeves
from .spaces.animal import Animal
from .spaces.land import Land
from .spaces.manure import Manure

from sandbox import settings


class DecisionSpace(object):
    def __init__(self):
        """ Base class for all decision spaces in the optimizer engine
        Represent the variables that make up the decision space along with their upper and lower bounds.

        A DecisionSpace holds:
            - tables with IDs and names for lrsegs, counties, agencies, sectors, loadsources, BMPs
        A DecisionSpace can perform these actions:
            - construct itself from a specified geography or geoagencysector table
            - QC itself

        """
        # SourceHooks
        self.jeeves = self.load_queries()

        # Shared Components for decision space
        self.baseconditionid = None
        self.lrsegids = None  # an LRSeg list for this instance
        self.countyids = None  # a County list for this instance
        self.agencyids = None  # list of agencies selected to specify free parameter groups
        self.sectorids = None  # list of sectors selected to specify free parameter groups

        self.animal = Animal(jeeves=self.jeeves)
        self.land = Land(jeeves=self.jeeves)
        self.manure = Manure(jeeves=self.jeeves)

    def __iter__(self):
        """ Generator to return the decision space names and decision space objects, e.g. in For loops """
        for x, y in zip(['animal', 'land', 'manure'],
                        [self.animal, self.land, self.manure]):
            yield x, y

    # Generation Recipes
    def proceed_to_decision_space_from_geography(self, scale=None, areanames=None, baseconditionid=None):
        """ Generate a decision space from just a geography (scale + area names)

        Note:
            This will include all agencies, all loadsources, and all bmps.
        """
        if settings.verbose:
            print('** %s DecisionSpace being generated from geography **' % type(self).__name__)
        # Metadata to BMPs

        self.populate_geography_from_scale_and_areas(scale=scale, areanames=areanames)
        # Populate Agencies from Geography
        # i.e. make la_table from lrsegids alone
        lrseg_agency_table = self.jeeves.agency.append_agencyid_to_lrsegidtable(lrsegids=self.lrsegids)
        self.agencyids = lrseg_agency_table.loc[:, ['agencyid']]
        # Populate Sectors
        self.sectorids = self.jeeves.sector.all_ids()

        # Populate Load Sources
        source_lrseg_agency_table = self.jeeves.loadsource.\
            sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=lrseg_agency_table,
                                                               sectorids=self.sectorids)
        source_county_agency_table = self.jeeves.loadsource.\
            sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=source_lrseg_agency_table)
        # Generate DecisionSpace
        for dsname, ds in self:
            # Set basecondition
            ds.baseconditionid = baseconditionid

            ds.agencyids = self.agencyids
            ds.sectorids = self.sectorids
            ds.lrseg_agency_table = lrseg_agency_table
            ds.source_lrseg_agency_table = source_lrseg_agency_table
            ds.source_county_agency_table = source_county_agency_table

            ds.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=ds.lrseg_agency_table,
                                                              sectorids=ds.sectorids)

    def proceed_to_decision_space_from_geoagencysectorids(self):
        """ Generate a decision space from pre-defined geography (scale + area names), agency, and sector ids.
        """
        if settings.verbose:
            print('** DecisionSpace being generated from geography, agencies, sectors **')

        # make la_table when agencyids have already been populated """
        all_lrseg_agencyids_table = self.jeeves.agency.append_agencyid_to_lrsegidtable(lrsegids=self.lrsegids)
        columnmask = ['lrsegid', 'agencyid']

        lrseg_agency_table = all_lrseg_agencyids_table.loc[:, columnmask].merge(self.agencyids, how='inner')

        # Populate Load Sources
        source_lrseg_agency_table = self.jeeves.loadsource.\
            sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=lrseg_agency_table,
                                                               sectorids=self.sectorids)
        source_county_agency_table = self.jeeves.loadsource.\
            sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=source_lrseg_agency_table)

        for dsname, ds in self:
            ds.lrseg_agency_table = lrseg_agency_table
            ds.source_lrseg_agency_table = source_lrseg_agency_table
            ds.source_county_agency_table = source_county_agency_table
            # Generate DecisionSpace
            ds.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=ds.lrseg_agency_table,
                                                              sectorids=ds.sectorids)

    def populate_geography_from_scale_and_areas(self, scale=None, areanames=None):
        self.lrsegids = self.jeeves.geo.lrsegids_from_geoscale_with_names(scale=scale, areanames=areanames)
        self.countyids = self.jeeves.geo.countyids_from_lrsegids(lrsegids=self.lrsegids)
        for dsname, ds in self:
            ds.lrsegids = self.lrsegids
            ds.countyids = self.countyids

    @staticmethod
    def load_queries():
        # SourceHooks
        return Jeeves()
