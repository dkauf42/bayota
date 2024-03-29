import pandas as pd
import warnings

from .sourcehooks import SourceHook


class Lrseg(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Methods for querying CAST data related to Land River Segments """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

    def all_names(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblLandRiverSegment', col='landriversegment', astype=astype)

    def all_ids(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblLandRiverSegment', col='lrsegid', astype=astype)

    def ids_from_names(self, names=None):
        return self._map_using_sourcetbl(names, tbl='TblLandRiverSegment',
                                         fromcol='landriversegment', tocol='lrsegid')

    def names_from_ids(self, ids=None):
        return self._map_using_sourcetbl(ids, tbl='TblLandRiverSegment',
                                         fromcol='lrsegid', tocol='landriversegment')

    def totalacres_for(self, lrsegnames=None, lrsegids=None):
        if lrsegnames is not None:
            names = self.forceToSingleColumnDataFrame(lrsegnames, colname='landriversegment')

            subtbl = self.singleconvert(sourcetbl='TblLandRiverSegment',
                                        toandfromheaders=['totalacres', 'landriversegment'],
                                        fromtable=names, toname='totalacres')

        elif lrsegids is not None:
            names = self.forceToSingleColumnDataFrame(lrsegnames, colname='lrsegid')

            subtbl = self.singleconvert(sourcetbl='TblLandRiverSegment',
                                        toandfromheaders=['totalacres', 'lrsegid'],
                                        fromtable=names, toname='totalacres')

        else:
            raise ValueError('No valid input passed')

        return list(subtbl['totalacres'])

    def append_lrsegs_to_counties(self, tablewithcountyids):
        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data

        columnmask = ['countyid', 'lrsegid', 'landriversegment']
        tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(tablewithcountyids, how='inner')

        return tblsubset

    def remove_outofcbws_lrsegs(self, lrseglist=None, lrsegdf=None):
        TblLandRiverSegment = self.source.TblLandRiverSegment  # get relevant source data

        if lrseglist is not None:
            tablewithlrsegs = self.forceToSingleColumnDataFrame(lrseglist, colname='landriversegment')

            columnmask = ['landriversegment', 'outofcbws']
            tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(tablewithlrsegs, how='inner')

            newsubset = tblsubset.loc[tblsubset['outofcbws'] != True, 'landriversegment'].tolist()

            return newsubset
        elif lrsegdf is not None:
            tablewithlrsegs = lrsegdf

            columnmask = ['landriversegment', 'outofcbws']
            tblsubset = TblLandRiverSegment.loc[:, columnmask].merge(tablewithlrsegs, how='inner')

            newsubset = tblsubset.loc[tblsubset['outofcbws'] != True, :]

            return newsubset

    def lrsegids_from(self, lrsegnames=None, countystatestrs=None, countyid=None):
        kwargs = (lrsegnames, countystatestrs, countyid)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if self.checkOnlyOne(kwargsNoDataFrames) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if lrsegnames is not None:
            return self.ids_from_names(names=lrsegnames)
        elif countystatestrs is not None:
            return self.__lrsegids_from_countystatestrs(getfrom=countystatestrs)
        elif countyid is not None:
            return self.__lrsegids_from_countyid(getfrom=countyid)
        else:
            raise ValueError('unrecognized input')