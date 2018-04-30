import pandas as pd

from sandbox import settings


class Space(object):
    def __init__(self, jeeves=None, lrsegids=None, countyids=None):
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
        self.baseconditionid = None
        self.lrsegids = lrsegids  # an LRSeg list for this instance
        self.countyids = countyids  # a County list for this instance
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

    def set_idtable_fromSourceGeoAgency(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def qc_loadsources(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def populate_bmps(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def qc_bmps(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def append_bounds(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def translate_ids_to_names(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def populate_decisionspace_from_lrseg_agency_table(self, lrsegagencyidtable=None, sectorids=None):
        if settings.verbose:
            print('\t-- appending loadsources to the lrseg,agency,sector table, which looks like:')
            print(lrsegagencyidtable.head())
            print('\t^shape is %s' % str(lrsegagencyidtable.shape))
            print('\t--')

        # QC LoadSources
        self.set_idtable_fromSourceGeoAgency()
        self.qc_loadsources()

        if settings.verbose:
            print('\t-- appending bmps to the source,lrseg,agency,sector table, which looks like:')
            print(self.source_lrseg_agency_table.head())
            print('\t^shape is %s' % str(self.source_lrseg_agency_table.shape))
            print('\t--')
        # Populate BMPs
        self.populate_bmps()
        # QC BMPs
        self.qc_bmps()
        self.append_bounds()
        self.translate_ids_to_names()

        if settings.verbose:
            print('\t-- after qc_bmps and translation, the idtable looks like')
            print(self.idtable.head())
            print('\t^shape is %s' % str(self.idtable.shape))
            print('\t--')
