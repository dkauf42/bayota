import pandas as pd
from sandbox.util.decisionspace.spaces.spaces import Space
from sandbox import settings


class Manure(Space):
    def __init__(self, jeeves=None):
        """ Manure Decision Space

        the idtable for manure is characterized as a 'sftab' table, i.e.
        S(ource), F(rom-FIPS), T(o-FIPS), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.\
            manure_sftabidtable_from_SourceFromToAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                               source_county_agency_table,
                                                               baseconditionid=self.baseconditionid)

    def translate_ids_to_names(self):
        # Translate to names
        self.nametable = self.jeeves.translator.translate_sftabidtable_to_sftabnametable(self.idtable)

    def qc(self):
        """ Remove LoadSources or BMPs that the optimization engine should not modify

        The following LoadSources are removed from the decision space:
        - AllLoadSources

        """
        if settings.verbose:
            print('OptCase.qaqc_manure_decisionspace(): QA/QCing...')
            print('Decision Space Table size: %s' % (self.idtable.shape, ))

        origrowcnt, origcolcnt = self.idtable.shape

        removaltotal = 0

        # Remove "AllLoadSources" loadsourcegroup from the manure table
        loadsourcenametoremove = 'AllLoadSources'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.idtable['loadsourcegroupid'] == loadsourcegroupid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove "FEEDPermitted" and "FEEDNonPermitted" loadsourcegroups from the manure table,
        # leaving only "FEED", which contains both anyway
        loadsourcenametoremove = 'FEEDPermitted'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.idtable['loadsourcegroupid'] == loadsourcegroupid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))
        loadsourcenametoremove = 'FEEDNonPermitted'
        loadsourcegroupid = self.jeeves.loadsource. \
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.idtable['loadsourcegroupid'] == loadsourcegroupid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove any duplicate rows. (these are created when loadsourceids are matched to loadsourcegroupids
        print('OptCase.qaqc_manure_decisionspace():')
        print(self.idtable.head())
        self.idtable.drop_duplicates()
        print(self.idtable.head())

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


