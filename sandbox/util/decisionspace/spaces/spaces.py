import collections
import pandas as pd

from sandbox import settings


class Space(object):
    def __init__(self, jeeves=None):
        """ Base class for all decision spaces in the optimizer engine
        Represent the variables that make up the decision space along with their upper and lower bounds.

        A DecisionSpace holds:
            - tables with IDs and names for lrsegs, counties, agencies, sectors, loadsources, BMPs
        A DecisionSpace can perform these actions:
            - construct itself from a specified geography or geoagencysector table
            - QC itself

        Attributes:
            name (str):
            idtable (pd.DataFrame):
            nametable (pd.DataFrame):

        """
        self.name = ''
        self.specs = None

        # Jeeves provides hooks to query the source data
        self.jeeves = jeeves

        # Primary decision space tables
        self.idtable = None
        self.nametable = None

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

    def __repr__(self):
        """ Custom 'print' that displays the decision space details
        """
        d = self.__dict__

        formattedstr = "\n***** Decision Space Details *****\n" \
                       "name:                     %s\n" \
                       "# of lrsegs:              %s\n" \
                       "agencies included:        %s\n" \
                       "sectors included:         %s\n" \
                       "************************************\n" %\
                       tuple([str(i) for i in [d['name'],
                                               d['lrsegids'],
                                               d['agencyids'],
                                               d['sectorids']
                                               ]
                              ])

        return formattedstr

    def populate_bmps(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def qc(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def append_bounds(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    # Generation Recipes
    def proceed_from_geography_to_decision_space(self, scale=None, areanames=None):
        """ Generate a decision space from just a geography (scale + area names)

        Note:
            This will include all agencies, all loadsources, and all bmps.
        """
        # Metadata to BMPs
        self.populate_geography_from_scale_and_areas(scale=scale, areanames=areanames)

        # Populate Agencies from Geography
        # i.e. make la_table from lrsegids alone
        self.lrseg_agency_table = self.jeeves.agency.agencylrsegidtable_from_lrsegids(lrsegids=self.lrsegids)
        self.agencyids = self.lrseg_agency_table.loc[:, ['agencyid']]

        # Populate Sectors
        self.sectorids = self.jeeves.sector.all_ids()

        # Generate DecisionSpace
        self.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=self.lrseg_agency_table,
                                                            sectorids=self.sectorids)

    def proceed_from_geoagencysectorids_to_decision_space(self):
        """ Generate a decision space from pre-defined geography (scale + area names), agency, and sector ids.
        """
        # make la_table when agencyids have already been populated """
        all_lrseg_agencyids_table = self.jeeves.agency.agencylrsegidtable_from_lrsegids(lrsegids=self.lrsegids)

        columnmask = ['lrsegid', 'agencyid']
        self.lrseg_agency_table = all_lrseg_agencyids_table.loc[:, columnmask].merge(self.agencyids, how='inner')

        # Generate DecisionSpace
        self.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=self.lrseg_agency_table,
                                                            sectorids=self.sectorids)

    # Generation steps
    def populate_decisionspace_from_lrseg_agency_table(self, lrsegagencyidtable=None, sectorids=None):
        # Populate Load Sources
        self.source_lrseg_agency_table = self.jeeves.loadsource.\
            sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=lrsegagencyidtable,
                                                               sectorids=sectorids)
        self.source_county_agency_table = self.jeeves.loadsource.\
            sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=self.
                                                                    source_lrseg_agency_table)
        # Populate BMPs
        self.populate_bmps()
        # QC
        self.qc()
        self.append_bounds()

    def populate_geography_from_scale_and_areas(self, scale=None, areanames=None):
        self.lrsegids = self.jeeves.geo.lrsegids_from_geoscale_with_names(scale=scale, areanames=areanames)
        self.countyids = self.jeeves.geo.countyids_from_lrsegids(lrsegids=self.lrsegids)
        # TODO REPLACE ^ WITH:  self.queries.countyids_from_lrsegids(lrsegids=self.lrsegids)

    # GUI API
    def set_freeparamgrps(self, agencycodes=None, sectornames=None):
        self.agencyids = self.jeeves.agency.ids_from_names(agencycodes=agencycodes)
        self.sectorids = self.jeeves.sector.ids_from_names(names=sectornames)
