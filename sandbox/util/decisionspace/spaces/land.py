import pandas as pd
from sandbox.util.decisionspace.spaces.spaces import Space
from sandbox import settings


class Land(Space):
    def __init__(self, jeeves=None, baseconditionid=None,
                 lrsegids=None, countyids=None, agencyids=None, sectorids=None,
                 lrseg_agency_table=None, source_lrseg_agency_table=None, source_county_agency_table=None):
        """ Land Decision Space

        the idtable for land is characterized as a 'slab' table, i.e.
        S(ource), L(andriversegment), A(gency), B(mp)

        """
        Space.__init__(self, jeeves=jeeves, baseconditionid=baseconditionid,
                       lrsegids=lrsegids, countyids=countyids,
                       agencyids=agencyids, sectorids=sectorids,
                       lrseg_agency_table=lrseg_agency_table, source_lrseg_agency_table=source_lrseg_agency_table,
                       source_county_agency_table=source_county_agency_table)

    def append_bmps_to_SourceGeoAgencytable(self):
        """ Append the BMPs to the decision space table """
        # get IDs
        self.idtable = self.jeeves.bmp.append_land_bmpids(table_with_loadsourceids=self.source_lrseg_agency_table)

    def translate_ids_to_names(self):
        # Translate to names
        self.nametable = self.jeeves.translator.translate_slabidtable_to_slabnametable(self.idtable)

    def qc_bmps(self):
        """ Remove BMPs that the optimization engine should not modify

        The following BMPs are removed from the decision space:
        - Urban Stream Restoration Protocol
        - Non-Urban Stream Restoration Protocol
        - Stormwater Performance Standards (RR [runoff reduction] and ST [stormwater treatment])
        - Land policy BMPs

        """
        if settings.verbose:
            print('\t-- QC\'ing the idtable { in land.qc_bmps() }, which looks like:')
            print(self.idtable.head())
            print('^shape is %s' % (self.idtable.shape, ))

        origrowcnt, origcolcnt = self.idtable.shape
        newtable = self.idtable

        removaltotal = 0

        # Identify land BMPs that should be excluded because
        # they are already affected when a land use change BMP is applied
        #  (This is based on an email conversation w/Jess on 8 May 2018
        #   [subject: "question: Efficiency parts of land use change BMPs"]
        #   and a convo w/Olivia on 2 May 2018 [subject: "quick followup"])
        uplandbmpstoexclude = self.jeeves.bmp.get_land_uplandbmps_to_exclude()

        # It's fine to include PoultRed for now:
        uplandbmpstoexclude = uplandbmpstoexclude.drop(
            uplandbmpstoexclude[uplandbmpstoexclude['bmpshortname'] == 'PoultRed'].index)

        singlebmpstoremove = ['UrbStrmRestPro',  # "Urban Stream Restoration Protocol"
                              'NonUrbStrmRestPro',  # "Non-Urban Stream Restoration Protocol"
                              ] + uplandbmpstoexclude['bmpshortname'].tolist()

        for bmpnametoremove in singlebmpstoremove:
            bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
            bmptypename = self.jeeves.bmp.single_bmptype_from_bmpid(bmpid=bmpid)
            mask = pd.Series(newtable['bmpid'] == bmpid)
            newtable = newtable[~mask]
            removaltotal += mask.sum()
            if settings.verbose:
                print('removing %d for %s (type=%s)' % (mask.sum(), bmpnametoremove, bmptypename))

        """
        "Stormwater Performance Standard" BMPs (RR [runoff reduction] and ST [stormwater treatment])
        ^
        shouldn’t be excluded, but need assumed values for two of their three inputs
        """
        # # Remove "Stormwater Performance Standard" BMPs (RR [runoff reduction] and ST [stormwater treatment])
        # bmpnametoremove = 'RR'
        # bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        # mask = pd.Series(newtable['bmpid'] == bmpid)
        # newtable = newtable[~mask]
        # removaltotal += mask.sum()
        # if settings.verbose:
        #     print('removing %d for %s' % (mask.sum(), bmpnametoremove))
        #
        # bmpnametoremove = 'ST'
        # bmpid = self.jeeves.bmp.single_bmpid_from_shortname(bmpshortname=bmpnametoremove)
        # mask = pd.Series(newtable['bmpid'] == bmpid)
        # newtable = newtable[~mask]
        # removaltotal += mask.sum()
        # if settings.verbose:
        #     print('removing %d for %s' % (mask.sum(), bmpnametoremove))

        # Remove Policy BMPs
        bmpids = self.jeeves.bmp.bmpids_from_categoryids(categoryids=[4])
        mask = pd.Series(newtable['bmpid'].isin(bmpids.bmpid.tolist()))
        # TODO: replace the above '4' with a call that gets the number from a string such as 'Land Policy BMPs'
        newtable = newtable[~newtable['bmpid'].isin(bmpids.bmpid.tolist())]
        removaltotal += mask.sum()
        if settings.verbose:
            print('removing %d for %s' % (mask.sum(), 'Land Policy BMPs'))

        self.idtable = newtable
        newrowcnt, newcolcnt = self.idtable.shape
        if settings.verbose:
            print('New decision space size is (%d, %d) - (%d, ) = (%d, %d)' %
                  (origrowcnt, origcolcnt, removaltotal, newrowcnt, newcolcnt))

    def append_units_and_bounds(self):
        self.idtable = self.jeeves.bmp.append_unitids_to_table_with_bmpids(bmpidtable=self.idtable)

        # unitid_to_ranges = {'percent': [0, 100]}

        # The bound columns are created with default values to be replaced.
        self.idtable['lowerbound'] = 0
        self.idtable['upperbound'] = 100

        self.idtable[self.idtable['bmpunitfullname'] == 'percent']['lowerbound'] = 0
        self.idtable[self.idtable['bmpunitfullname'] == 'percent']['upperbound'] = 100
        self.idtable[self.idtable['bmpunitfullname'] == 'acres']['lowerbound'] = 0
        self.idtable[self.idtable['bmpunitfullname'] == 'acres']['upperbound'] = 999999
        # For Acres: Add all of the acres (across LoadSources) from "TblLandUsePreBmp"
        return self.idtable.copy()

        # self.land_decisionspace = self.queries. \
        #     appendBounds_to_land_slabidtable(slabidtable=self.land_slabidtable)
