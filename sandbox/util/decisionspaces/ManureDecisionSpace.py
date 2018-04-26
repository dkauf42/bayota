from .decisionspace import DecisionSpace
from sandbox import settings


class ManureDecisionSpace(DecisionSpace):
    def __init__(self):
        DecisionSpace.__init__(self)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.manure_sftabidtable = self.jeeves.bmp.\
            manure_sftabidtable_from_SourceFromToAgencyIDtable(SourceCountyAgencyIDtable=self.
                                                               source_county_agency_table,
                                                               baseconditionid=self.baseconditionid)
        # Translate to names
        self.manure_sftabnametable = self.jeeves.translator.\
            translate_sftabidtable_to_sftabnametable(self.manure_sftabidtable)

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
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.manure_sftabidtable['loadsourcegroupid'] == loadsourcegroupid)
        self.manure_sftabidtable = self.manure_sftabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))

        # Remove "FEEDPermitted" and "FEEDNonPermitted" loadsourcegroups from the manure table,
        # leaving only "FEED", which contains both anyway
        loadsourcenametoremove = 'FEEDPermitted'
        loadsourcegroupid = self.jeeves.loadsource.\
            single_loadsourcegroupid_from_loadsourcegroup_name(loadsourcegroupname=loadsourcenametoremove)
        mask = pd.Series(self.manure_sftabidtable['loadsourcegroupid'] == loadsourcegroupid)
        self.manure_sftabidtable = self.manure_sftabidtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), loadsourcenametoremove))
        loadsourcenametoremove = 'FEEDNonPermitted'
        loadsourcegroupid = self.jeeves.loadsource. \
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


