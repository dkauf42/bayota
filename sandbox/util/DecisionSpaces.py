import collections
import pandas as pd

from .Jeeves import Agency
from .Jeeves import Bmp
from .Jeeves import Geo
from .Jeeves import LoadSource
from .Jeeves import Metadata
from .Jeeves import Sector
from .Jeeves import Translator

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
        self.name = ''
        self.specs = None

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
        # For land bmps (no bounds yet)
        self.land_slabidtable = None
        self.land_slabnametable = None
        # For animal bmps (no bounds yet)
        self.animal_scabidtable = None
        self.animal_scabnametable = None
        # For manure bmps (no bounds yet)
        self.manure_sftabidtable = None
        self.manure_sftabnametable = None

        # SourceHooks
        self.agency = Agency()
        self.bmp = Bmp()
        self.geo = Geo()
        self.loadsource = LoadSource()
        self.sector = Sector()
        self.translator = Translator()

    def __repr__(self):
        """ Custom 'print' that displays the decision space details
        """
        d = self.__dict__

        formattedstr = "\n***** Decision Space Details *****\n" \
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
    def proceed_from_geography_to_decision_space(self):
        """ Generate a decision space from just a geography (scale + area names)

        Note:
            This will include all agencies, all loadsources, and all bmps.
        """
        # Metadata to BMPs
        self.populate_geography_from_scale_and_areas()

        # Populate Agencies from Geography
        # i.e. make la_table from lrsegids alone
        self.lrseg_agency_table = self.agency.agencylrsegidtable_from_lrsegids(lrsegids=self.lrsegids)
        self.agencyids = self.lrseg_agency_table.loc[:, ['agencyid']]

        # Populate Sectors
        self.sectorids = self.sector.all_ids()

        # Generate DecisionSpace
        self.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=self.lrseg_agency_table,
                                                            sectorids=self.sectorids)

    def proceed_from_geoagencysectorids_to_decision_space(self):
        """ Generate a decision space from pre-defined geography (scale + area names), agency, and sector ids.
        """
        # make la_table when agencyids have already been populated """
        all_lrseg_agencyids_table = self.agency.agencylrsegidtable_from_lrsegids(lrsegids=self.lrsegids)

        columnmask = ['lrsegid', 'agencyid']
        self.lrseg_agency_table = all_lrseg_agencyids_table.loc[:, columnmask].merge(self.agencyids, how='inner')

        # Generate DecisionSpace
        self.populate_decisionspace_from_lrseg_agency_table(lrsegagencyidtable=self.lrseg_agency_table,
                                                            sectorids=self.sectorids)

    # Generation steps
    def populate_decisionspace_from_lrseg_agency_table(self, lrsegagencyidtable=None, sectorids=None):
        # Populate Load Sources
        self.source_lrseg_agency_table = self.loadsource.\
            sourceLrsegAgencyIDtable_from_lrsegAgencySectorids(lrsegagencyidtable=lrsegagencyidtable,
                                                               sectorids=sectorids)
        self.source_county_agency_table = self.loadsource.\
            sourceCountyAgencyIDtable_from_sourceLrsegAgencyIDtable(sourceAgencyLrsegIDtable=self.
                                                                    source_lrseg_agency_table)
        # Populate BMPs
        self.populate_bmps()
        # QC
        self.qc()
        self.append_bounds()

    def populate_geography_from_scale_and_areas(self, scale=None, areanames=None):
        self.lrsegids = self.geo.lrsegids_from_geoscale_with_names(scale=scale,
                                                                   areanames=areanames)
        self.countyids = self.geo.countyids_from_lrsegids(lrsegids=self.lrsegids)
        # TODO REPLACE ^ WITH:  self.queries.countyids_from_lrsegids(lrsegids=self.lrsegids)

    # GUI API
    def set_freeparamgrps(self, agencycodes=None, sectornames=None):
        self.agencyids = self.agency.ids_from_names(agencycodes=agencycodes)
        self.sectorids = self.sector.ids_from_names(names=sectornames)


class LandDecisionSpace(DecisionSpace):
    def __init__(self):
        DecisionSpace.__init__(self)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.land_slabidtable = self.bmp.\
            land_slabidtable_from_SourceLrsegAgencyIDtable(SourceLrsegAgencyIDtable=self.
                                                           source_lrseg_agency_table)
        # Translate to names
        self.land_slabnametable = self.translator.translate_slabidtable_to_slabnametable(self.land_slabidtable)

    def qc(self):
        """ Remove BMPs that the optimization engine should not modify

        The following BMPs are removed from the decision space:
        - Urban Stream Restoration Protocol
        - Non-Urban Stream Restoration Protocol
        - Stormwater Performance Standards (RR [runoff reduction] and ST [stormwater treatment])
        - Land policy BMPs

        """
        if settings.verbose:
            print('OptCase.qaqc_land_decisionspace(): QA/QCing...')
            print('Decision Space Table size: %s' % (self.land_slabidtable.shape, ))

        origrowcnt, origcolcnt = self.land_slabidtable.shape

        removaltotal = 0

        # Remove "Urban Stream Restoration Protocol" BMP
        bmpnametoremove = 'UrbStrmRestPro'
        bmpid = Bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove "Non-Urban Stream Restoration Protocol" BMP
        bmpnametoremove = 'NonUrbStrmRestPro'
        bmpid = Bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove "Stormwater Performance Standard" BMPs (RR [runoff reduction] and ST [stormwater treatment])
        bmpnametoremove = 'RR'
        bmpid = Bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        bmpnametoremove = 'ST'
        bmpid = Bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.land_slabidtable['bmpid'] == bmpid)
        self.land_slabidtable = self.land_slabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove Policy BMPs
        bmpids = Bmp.bmpids_from_categoryids(categoryids=[4])
        mask = pd.Series(self.land_slabidtable['bmpid'].isin(bmpids.bmpid.tolist()))
        # TODO: replace the above '4' with a call that gets the number from a string such as 'Land Policy BMPs'
        self.land_slabidtable = self.land_slabidtable[~self.land_slabidtable['bmpid'].isin(bmpids.bmpid.tolist())]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), 'Land Policy BMPs'))

        newrowcnt, newcolcnt = self.land_slabidtable.shape
        if settings.verbose:
            print('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                  (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def append_bounds(self):
        self.slabidtable['lowerbound'] = 0
        self.slabidtable['upperbound'] = 100
        # For Acres: Add all of the acres (across LoadSources) from "TblLandUsePreBmp"
        return self.slabidtable.copy()

        # self.land_decisionspace = self.queries. \
        #     appendBounds_to_land_slabidtable(slabidtable=self.land_slabidtable)


class AnimalDecisionSpace(DecisionSpace):
    def __init__(self):
        DecisionSpace.__init__(self)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.animal_scabidtable = self.bmp.\
            animal_scabidtable_from_SourceCountyAgencyIDtable(SourceCountyAgencyIDtable=self.source_county_agency_table,
                                                              baseconditionid=self.baseconditionid)
        # Translate to names
        self.animal_scabnametable = self.translator.translate_scabidtable_to_scabnametable(self.animal_scabidtable)

    def qc(self):
        pass

    def append_bounds(self):
        self.scabidtable['lowerbound'] = 0
        self.scabidtable['upperbound'] = 100
        # For Animals: Add...?
        return self.scabidtable.copy()
        # self.animal_decisionspace = self.queries.\
        #     appendBounds_to_animal_scabidtable(scabidtable=self.animal_scabidtable)


class ManureDecisionSpace(DecisionSpace):
    def __init__(self):
        DecisionSpace.__init__(self)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.manure_sftabidtable = self.bmp.\
            manure_sftabidtable_from_SourceFromToAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                                            source_county_agency_table,
                                                                            baseconditionid=self.baseconditionid)
        # Translate to names
        self.manure_sftabnametable = self.translator.translate_sftabidtable_to_sftabnametable(self.manure_sftabidtable)

    def qc(self):
        """ Remove LoadSources or BMPs that the optimization engine should not modify

        The following LoadSources are removed from the decision space:
        - AllLoadSources

        """
        if settings.verbose:
            print('OptCase.qaqc_manure_decisionspace(): QA/QCing...')
            print('Decision Space Table size: %s' % (self.manure_sftabidtable.shape, ))

        origrowcnt, origcolcnt = self.manure_sftabidtable.shape

        removaltotal = 0

        # Remove "AllLoadSources" loadsourcegroup from the manure table
        loadsourcenametoremove = 'AllLoadSources'
        loadsourcegroupid = LoadSource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.manure_sftabidtable['loadsourcegroupid'] == loadsourcegroupid)
        self.manure_sftabidtable = self.manure_sftabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove "FEEDPermitted" and "FEEDNonPermitted" loadsourcegroups from the manure table,
        # leaving only "FEED", which contains both anyway
        loadsourcenametoremove = 'FEEDPermitted'
        loadsourcegroupid = LoadSource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.manure_sftabidtable['loadsourcegroupid'] == loadsourcegroupid)
        self.manure_sftabidtable = self.manure_sftabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))
        loadsourcenametoremove = 'FEEDNonPermitted'
        loadsourcegroupid = LoadSource. \
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.manure_sftabidtable['loadsourcegroupid'] == loadsourcegroupid)
        self.manure_sftabidtable = self.manure_sftabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove any duplicate rows. (these are created when loadsourceids are matched to loadsourcegroupids
        print('OptCase.qaqc_manure_decisionspace():')
        print(self.manure_sftabidtable.head())
        self.manure_sftabidtable.drop_duplicates()
        print(self.manure_sftabidtable.head())

        newrowcnt, newcolcnt = self.manure_sftabidtable.shape
        if settings.verbose:
            print('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                  (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def append_bounds(self):
        self.sftabidtable['lowerbound'] = 0
        self.sftabidtable['upperbound'] = 100
        # For Dry_Tons_of_Stored_Manure: Add...?
        return self.sftabidtable.copy()
        # self.manure_decisionspace = self.queries.\
        #     appendBounds_to_manure_sftabidtable(sftabidtable=self.manure_sftabidtable)


