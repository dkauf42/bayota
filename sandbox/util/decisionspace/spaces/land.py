import pandas as pd
from sandbox.util.decisionspace.spaces.spaces import Space
from sandbox import settings


class Land(Space):
    def __init__(self, jeeves=None):
        """ Land Decision Space

        the idtable for land is characterized as a 'slab' table, i.e.
        S(ource), L(andriversegment), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves)

    def populate_bmps(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.\
            land_slabidtable_from_SourceLrsegAgencyIDtable(SourceLrsegAgencyIDtable=self.
                                                           source_lrseg_agency_table)
        # Translate to names
        self.nametable = self.jeeves.translator.translate_slabidtable_to_slabnametable(self.idtable)

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
            print('Decision Space Table size: %s' % (self.idtable.shape, ))

        origrowcnt, origcolcnt = self.idtable.shape

        removaltotal = 0

        # Remove "Urban Stream Restoration Protocol" BMP
        bmpnametoremove = 'UrbStrmRestPro'
        bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.idtable['bmpid'] == bmpid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove "Non-Urban Stream Restoration Protocol" BMP
        bmpnametoremove = 'NonUrbStrmRestPro'
        bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.idtable['bmpid'] == bmpid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove "Stormwater Performance Standard" BMPs (RR [runoff reduction] and ST [stormwater treatment])
        bmpnametoremove = 'RR'
        bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.idtable['bmpid'] == bmpid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        bmpnametoremove = 'ST'
        bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        mask = pd.Series(self.idtable['bmpid'] == bmpid)
        self.idtable = self.idtable[~mask]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove Policy BMPs
        bmpids = self.jeeves.bmp.bmpids_from_categoryids(categoryids=[4])
        mask = pd.Series(self.idtable['bmpid'].isin(bmpids.bmpid.tolist()))
        # TODO: replace the above '4' with a call that gets the number from a string such as 'Land Policy BMPs'
        self.idtable = self.idtable[~self.idtable['bmpid'].isin(bmpids.bmpid.tolist())]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), 'Land Policy BMPs'))

        newrowcnt, newcolcnt = self.idtable.shape
        if settings.verbose:
            print('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                  (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def append_bounds(self):
        self.idtable['lowerbound'] = 0
        self.idtable['upperbound'] = 100
        # For Acres: Add all of the acres (across LoadSources) from "TblLandUsePreBmp"
        return self.idtable.copy()

        # self.land_decisionspace = self.queries. \
        #     appendBounds_to_land_slabidtable(slabidtable=self.land_slabidtable)
