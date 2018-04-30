from sandbox.util.jeeves import Jeeves
from .spaces.animal import Animal
from .spaces.land import Land
from .spaces.manure import Manure

from sandbox import settings


class DecisionSpace(object):
    def __init__(self, jeeves=None, baseconditionid=None, lrsegids=None, countyids=None, agencyids=None, sectorids=None,
                 animalds=None, landds=None, manureds=None):
        """ Base class for all decision spaces in the optimizer engine
        Represent the variables that make up the decision space along with their upper and lower bounds.

        A DecisionSpace holds:
            - tables with IDs and names for lrsegs, counties, agencies, sectors, loadsources, BMPs
        A DecisionSpace can perform these actions:
            - construct itself from a specified geography or geoagencysector table
            - QC itself

        """
        # SourceHooks
        self.jeeves = jeeves

        # Shared Components for decision space
        self.baseconditionid = baseconditionid
        self.lrsegids = lrsegids  # an LRSeg list for this instance
        self.countyids = countyids  # a County list for this instance
        self.agencyids = agencyids  # list of agencies selected to specify free parameter groups
        self.sectorids = sectorids  # list of sectors selected to specify free parameter groups

        self.animal = animalds
        self.land = landds
        self.manure = manureds

    @classmethod
    def blank(cls):
        """ Constructor to generate an empty decision space

        Note:
            This will include all agencies, all loadsources, and all bmps.
        """
        if settings.verbose:
            print('** %s DecisionSpace being generated from geography **' % type(cls).__name__)

        # SourceHooks
        jeeves = cls.load_queries()

        # Set geography for each decision space
        cls.animal = Animal(jeeves=jeeves)
        cls.land = Land(jeeves=jeeves)
        cls.manure = Manure(jeeves=jeeves)

        return cls(jeeves=jeeves, animalds=cls.animal, landds=cls.land, manureds=cls.manure)

    @classmethod
    def fromgeo(cls, scale=None, areanames=None, baseconditionid=None):
        """ Constructor to generate a decision space from a geography (scale + area names)

        Note:
            This will include all agencies, all loadsources, and all bmps.
        """
        if settings.verbose:
            print('** %s DecisionSpace being generated from geography **' % type(cls).__name__)

        # SourceHooks
        jeeves = cls.load_queries()

        # Set geography for each decision space
        lrsegids = jeeves.geo.lrsegids_from_geoscale_with_names(scale=scale, areanames=areanames)
        countyids = jeeves.geo.countyids_from_lrsegids(lrsegids=lrsegids)
        cls.animal = Animal(jeeves=jeeves, lrsegids=lrsegids, countyids=countyids)
        cls.land = Land(jeeves=jeeves, lrsegids=lrsegids, countyids=countyids)
        cls.manure = Manure(jeeves=jeeves, lrsegids=lrsegids, countyids=countyids)

        # Populate Agencies from Geography (i.e. make la_table from lrsegids alone)
        lrseg_agency_table = jeeves.agency.append_agencyid_to_lrsegidtable(lrsegids=lrsegids)
        cls.agencyids = lrseg_agency_table.loc[:, ['agencyid']]

        # Populate Sectors
        cls.sectorids = jeeves.sector.all_ids()

        # Populate Load Sources
        source_lrseg_agency_table = jeeves.loadsource.\
            sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=lrseg_agency_table,
                                                               sectorids=cls.sectorids)
        source_county_agency_table = jeeves.loadsource.\
            sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=source_lrseg_agency_table)

        # Generate DecisionSpaces
        for ds in [cls.animal, cls.land, cls.manure]:
            # Set basecondition
            ds.baseconditionid = baseconditionid

            ds.agencyids = cls.agencyids
            ds.sectorids = cls.sectorids
            ds.lrseg_agency_table = lrseg_agency_table
            ds.source_lrseg_agency_table = source_lrseg_agency_table
            ds.source_county_agency_table = source_county_agency_table

            ds.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=ds.lrseg_agency_table,
                                                              sectorids=ds.sectorids)
        return cls(jeeves=jeeves, animalds=cls.animal, landds=cls.land, manureds=cls.manure,
                   lrsegids=lrsegids, countyids=countyids)

    def __iter__(self):
        """ Generator to return the decision space names and decision space objects, e.g. in For loops """
        for x, y in zip(['animal', 'land', 'manure'],
                        [self.animal, self.land, self.manure]):
            yield x, y

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

    # GUI API
    def set_freeparamgrps(self, agencycodes=None, sectornames=None):
        self.agencyids = self.jeeves.agency.ids_from_names(agencycodes=agencycodes)
        self.sectorids = self.jeeves.sector.ids_from_names(names=sectornames)
        for dsname, ds in self:
            ds.agencyids = self.agencyids
            ds.sectorids = self.sectorids

    # Generation steps
    def set_baseconditionid_from_name(self, name=''):
        self.baseconditionid = 1
        # TODO: replace this with a jeeves call to get a real ID number using a name argument

    @staticmethod
    def load_queries():
        # SourceHooks
        return Jeeves()
