import pandas as pd
from sandbox.util.decisionspace.spaces.spaces import Space
from sandbox import settings


class Manure(Space):
    def __init__(self, jeeves=None, baseconditionid=None,
                 lrsegids=None, countyids=None, agencyids=None, sectorids=None,
                 lrseg_agency_table=None, source_lrseg_agency_table=None, source_county_agency_table=None):
        """ Manure Decision Space

        the idtable for manure is characterized as a 'sftab' table, i.e.
        S(ource), F(rom-FIPS), T(o-FIPS), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves, baseconditionid=baseconditionid,
                       lrsegids=lrsegids, countyids=countyids,
                       agencyids=agencyids, sectorids=sectorids,
                       lrseg_agency_table=lrseg_agency_table, source_lrseg_agency_table=source_lrseg_agency_table,
                       source_county_agency_table=source_county_agency_table)

    def append_bmps_to_SourceGeoAgencytable(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.append_manure_bmpids(SourceFromToAgencyIDtable=self.source_county_agency_table,
                                                            baseconditionid=self.baseconditionid)

    def translate_ids_to_names(self):
        # Translate to names
        self.nametable = self.jeeves.translator.translate_sftabidtable_to_sftabnametable(self.idtable)

    def qc_bmps(self):
        """ Remove LoadSources or BMPs that the optimization engine should not modify

        The following LoadSources are removed from the decision space:
        - AllLoadSources
        - "FEEDPermitted" and "FEEDNonPermitted" are removed; replaced by "FEED"

        """
        if settings.verbose:
            print('\t-- QC\'ing the idtable { in manure.qc_bmps() }, which looks like:')
            print(self.idtable.head())
            print('^shape is %s' % (self.idtable.shape, ))

        origrowcnt, origcolcnt = self.idtable.shape
        newtable = self.idtable

        removaltotal = 0

        # Remove "AllLoadSources" loadsourcegroup from the manure table
        loadsourcenametoremove = 'AllLoadSources'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(newtable['loadsourcegroupid'] == loadsourcegroupid)
        newtable = newtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove "FEEDPermitted" and "FEEDNonPermitted" loadsourcegroups from the manure table,
        # leaving only "FEED", which contains both anyway
        loadsourcenametoremove = 'FEEDPermitted'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(newtable['loadsourcegroupid'] == loadsourcegroupid)
        newtable = newtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))
        loadsourcenametoremove = 'FEEDNonPermitted'
        loadsourcegroupid = self.jeeves.loadsource. \
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(newtable['loadsourcegroupid'] == loadsourcegroupid)
        newtable = newtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Add together the AnimalUnits and AnimalCount for Permitted and NonPermitted
        keycols = ['loadsourcegroupid', 'bmpid', 'baseconditionid', 'countyidFrom', 'countyidTo', 'animalid', 'agencyid']
        newtable = newtable.groupby(keycols)['animalcount', 'animalunits'].sum().reset_index()

        # Remove any duplicate rows. (these are created when loadsourceids are matched to loadsourcegroupids
        newtable.drop_duplicates()

        self.idtable = newtable
        newrowcnt, newcolcnt = self.idtable.shape
        if settings.verbose:
            print('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                  (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def append_bounds(self):
        self.idtable['lowerbound'] = 0
        self.idtable['upperbound'] = 100
        # For Dry_Tons_of_Stored_Manure: Add...?
        return self.idtable.copy()
        # self.manure_decisionspace = self.queries.\
        #     appendBounds_to_manure_sftabidtable(sftabidtable=self.manure_sftabidtable)


