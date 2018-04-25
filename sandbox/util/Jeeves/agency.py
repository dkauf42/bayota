from sandbox.util.Jeeves.sourcehooks import SourceHook


class Agency(SourceHook):
    def __init__(self):
        """ Agency Methods """
        SourceHook.__init__(self)

    def agencyids_from(self, agencycodes=None):
        agencycodes = self.forceToSingleColumnDataFrame(agencycodes, colname='agencycode')
        return self.singleconvert(sourcetbl='TblAgency', toandfromheaders=['agencycode', 'agencyid'],
                                  fromtable=agencycodes, toname='agencyid')

    def append_agencyid_to_lrsegids(self, lrsegids=None):
        TblLandRiverSegmentAgency = self.source.TblLandRiverSegmentAgency  # get relevant source data

        columnmask = ['lrsegid', 'agencyid']
        tblsubset = TblLandRiverSegmentAgency.loc[:, columnmask].merge(lrsegids, how='inner')

        return tblsubset.loc[:, ['lrsegid', 'agencyid']]

    def agencycodes_from_lrsegnames(self, lrsegnames=None):
        if not isinstance(lrsegnames, list):
            lrsegnames = lrsegnames.tolist()

        self.__ids_from_names(idtype='lrseg', names=lrsegnames)
        tblwithlrsegids = self.lrsegids_from(lrsegnames=lrsegnames)
        return self.agencycodes_from_lrsegids(lrsegids=tblwithlrsegids)

    def agencycodes_from_lrsegids(self, lrsegids=None):
        tblwithagencyids = self.append_agencyid_to_lrsegids(lrsegids=lrsegids).loc[:, ['agencyid']]

        return self.__singleconvert(sourcetbl='TblAgency', toandfromheaders=['agencycode', 'agencyid'],
                                    fromtable=tblwithagencyids, toname='agencycode')

    def all_agency_names(self):
        TblAgency = self.source.TblAgency  # get relevant source data
        return TblAgency.loc[:, 'agencycode']