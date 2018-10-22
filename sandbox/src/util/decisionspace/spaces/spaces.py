import logging
import pandas as pd

logger = logging.getLogger(__name__)


class Space(object):
    def __init__(self, jeeves=None, baseconditionid=None,
                 lrsegids=None, countyids=None, agencyids=None, sectorids=None,
                 lrseg_agency_table=None, source_lrseg_agency_table=None, source_county_agency_table=None):
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
        self.baseconditionid = baseconditionid
        self.lrsegids = lrsegids  # an LRSeg list for this instance
        self.countyids = countyids  # a County list for this instance
        self.agencyids = agencyids  # list of agencies selected to specify free parameter groups
        self.sectorids = sectorids  # list of sectors selected to specify free parameter groups

        # Intermediary tables for Decision Variable Space
        self.lrseg_agency_table = lrseg_agency_table
        self.source_lrseg_agency_table = source_lrseg_agency_table
        self.source_county_agency_table = source_county_agency_table

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

    def generate_from_SourceGeoAgencytable(self):
        logger.debug('** %s space being populated from lrseg_agency_table **  '
                     '{Space.generate_from_SourceGeoAgencytable()}' % type(self).__name__)

        # Populate BMPs
        self.append_bmps_to_SourceGeoAgencytable()
        logger.debug('\t-- idtable has  set to the Source,Geo,Agency table, which looks like:')
        logger.debug(self.idtable.head())
        logger.debug('\t^shape is %s' % str(self.idtable.shape))
        logger.debug('\t--')

        # QC BMPs
        self.qc_bmps()
        self.append_units_and_bounds()
        self.translate_ids_to_names()

        logger.debug('\t-- after qc_bmps and translation, the idtable looks like')
        logger.debug(self.idtable.head())
        logger.debug('\t^shape is %s' % str(self.idtable.shape))
        logger.debug('\t--')

    def append_bmps_to_SourceGeoAgencytable(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def qc_bmps(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def append_units_and_bounds(self):
        """ Overridden by land, animal, manure subclasses """
        pass

    def translate_ids_to_names(self):
        """ Overridden by land, animal, manure subclasses """
        pass
