from .sourcehooks import SourceHook
import pandas as pd

from .lrseg import Lrseg


class Agency(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Agency Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)

    def all_names(self):
        TblAgency = self.source.TblAgency  # get relevant source data
        return TblAgency.loc[:, 'agencycode']

    def ids_from_names(self, agencycodes=None):
        return self._map_using_sourcetbl(agencycodes, tbl='TblAgency',
                                         fromcol='agencycode', tocol='agencyid')

    def ids_from_fullnames(self, fullnames=None):
        return self._map_using_sourcetbl(fullnames, tbl='TblAgency',
                                         fromcol='agencyfullname', tocol='agencyid')

    def fullnames_from_ids(self, ids=None):
        return self._map_using_sourcetbl(ids, tbl='TblAgency',
                                         fromcol='agencyid', tocol='agencyfullname')

    def append_agencyid_to_lrsegids(self, lrsegids=None):
        TblLandRiverSegmentAgency = self.source.TblLandRiverSegmentAgency  # get relevant source data

        columnmask = ['lrsegid', 'agencyid']
        tblsubset = TblLandRiverSegmentAgency.loc[:, columnmask].merge(lrsegids, how='inner')

        return tblsubset.loc[:, ['lrsegid', 'agencyid']]

    def agencycodes_from_lrsegnames(self, lrsegnames=None):
        if not isinstance(lrsegnames, list):
            lrsegnames = lrsegnames.tolist()

        # self.__ids_from_names(idtype='lrseg', names=lrsegnames)
        lrsegids = self.lrseg.ids_from_names(names=lrsegnames)
        return self.agencycodes_from_lrsegids(lrsegids=lrsegids)

    def agencycodes_from_lrsegids(self, lrsegids=None):
        tblwithagencyids = self.append_agencyid_to_lrsegids(lrsegids=lrsegids).loc[:, ['agencyid']]

        return self.singleconvert(sourcetbl='TblAgency', toandfromheaders=['agencycode', 'agencyid'],
                                  fromtable=tblwithagencyids, toname='agencycode')

    def append_agencyid_to_lrsegidtable(self, lrsegids=None):
        TblLandRiverSegmentAgency = self.source.TblLandRiverSegmentAgency  # get relevant source data

        columnmask = ['lrsegid', 'agencyid']
        tblsubset = TblLandRiverSegmentAgency.loc[:, columnmask].merge(lrsegids, how='inner')

        return tblsubset.loc[:, ['lrsegid', 'agencyid']]

    def bounds_for_lrsegagencyparcels(self, idtable):
        TblUnit = self.source.TblUnit

        # TODO: generate code that sets bounds depending on the lrseg-agency parcel and unitid type
        # if unit==percent, then hard upper bound (HUB) is just 100
        # if unit==acres, impervious acres, or acre-feet, then HUB is the total acreage in la-parcel
        # if unit==feet, then HUB is the number of feet in the la-parcel
        # if unit==Lbs (of anything), then HUB is 9e19
        # if unit==oysters, then HUB is 9e19

        percentid = TblUnit[TblUnit['unit'] == 'percent']['unitid'].values[0]
        acresid = TblUnit[TblUnit['unit'] == 'acres']['unitid'].values[0]
        feetid = TblUnit[TblUnit['unit'] == 'feet']['unitid'].values[0]

        idtable[idtable['unitid'] == percentid]['upperbound'] = 100
        idtable[idtable['unitid'] == acresid]['upperbound'] = 976
        idtable[idtable['unitid'] == feetid]['upperbound'] = 33

        pass
