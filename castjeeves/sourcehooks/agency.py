from .sourcehooks import SourceHook
import pandas as pd

from .lrseg import Lrseg


class Agency(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Methods for querying CAST data related to Agencies """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)

    def all_names(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblAgency', col='agencycode', astype=astype)

    def all_ids(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblAgency', col='agencyid', astype=astype)

    def ids_from_names(self, agencycodes=None):
        """

        Args:
            agencycodes (list, pd.Series, or pd.DataFrame):

        Returns:
            same type as input
        """
        return self._map_using_sourcetbl(agencycodes, tbl='TblAgency',
                                         fromcol='agencycode', tocol='agencyid')

    def ids_from_fullnames(self, fullnames=None):
        """

        Args:
            fullnames (list, pd.Series, or pd.DataFrame):

        Returns:
            same type as input
        """
        return self._map_using_sourcetbl(fullnames, tbl='TblAgency',
                                         fromcol='agencyfullname', tocol='agencyid')

    def fullnames_from_ids(self, ids=None):
        """

        Args:
            ids (list, pd.Series, or pd.DataFrame):

        Returns:
            same type as input

        """
        return self._map_using_sourcetbl(ids, tbl='TblAgency',
                                         fromcol='agencyid', tocol='agencyfullname')

    def append_agencyid_to_lrsegids(self, lrsegids=None):
        return self.append_column_to_table(lrsegids, sourcetbl='TblLandRiverSegmentAgency',
                                           commoncol='lrsegid', appendcol='agencyid')

    def agencycodes_from_lrsegnames(self, lrsegnames=None):
        if not isinstance(lrsegnames, list):
            lrsegnames = lrsegnames.tolist()

        # self.__ids_from_names(idtype='lrseg', names=lrsegnames)
        lrsegids = self.lrseg.ids_from_names(names=lrsegnames)
        return self.agencycodes_from_lrsegids(lrsegids=lrsegids)

    def agencycodes_from_lrsegids(self, lrsegids=None):
        backtolist = False
        if isinstance(lrsegids, list):
            backtolist = True
            lrsegids = pd.DataFrame(lrsegids, columns=['lrsegid'])

        agencycodes = self._map_using_multiple_sourcetbls(lrsegids,
                                                          tbls=['TblLandRiverSegmentAgency', 'TblAgency'],
                                                          column_sequence=['lrsegid', 'agencyid', 'agencycode'])

        if backtolist:
            return agencycodes['agencycode'].tolist()
        else:
            return agencycodes

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
