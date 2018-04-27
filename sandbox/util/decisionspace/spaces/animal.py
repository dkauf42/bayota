import pandas as pd
from sandbox.util.decisionspace.spaces.spaces import Space
from sandbox import settings


class Animal(Space):
    def __init__(self, jeeves=None):
        """ Animal Decision Space

        the idtable for animal is characterized as a 'scab' table, i.e.
        S(ource), C(ounty), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves)

    def set_idtable_fromSourceGeoAgency(self):
        self.idtable = self.source_county_agency_table

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.\
            append_animal_bmpids_to_SourceCountyAgencyIDtable(SourceCountyAgencyIDtable=self.source_county_agency_table,
                                                              baseconditionid=self.baseconditionid)

    def translate_ids_to_names(self):
        # Translate to names
        self.nametable = self.jeeves.translator.translate_scabidtable_to_scabnametable(self.idtable)

    def qc_loadsources(self):
        pass

    def qc_bmps(self):
        """ Remove LoadSources or BMPs that the optimization engine should not modify

        The following LoadSources are removed from the decision space:
        - AllLoadSources
        - "FEEDPermitted" and "FEEDNonPermitted" are removed; replaced by "FEED"

        """
        if settings.verbose:
            print('manure.qc_bmps(): QCing...')
            print('Decision Space Table size: %s' % (self.idtable.shape, ))
            print(self.idtable)

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
        print('manure.qc_bmps():')
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
        # For Animals: Add...?
        return self.idtable.copy()
        # self.animal_decisionspace = self.queries.\
        #     appendBounds_to_animal_scabidtable(scabidtable=self.animal_scabidtable)

