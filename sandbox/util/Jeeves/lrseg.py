import pandas as pd
import warnings

from sandbox.util.Jeeves.sourcehooks import SourceHook


class Lrseg(SourceHook):
    def __init__(self):
        """ Geography Methods """
        SourceHook.__init__(self)

    def all_names(self):
        pass

    def all_ids(self):
        pass

    def ids_from_names(self, getfrom=None):
        getfrom = self.forceToSingleColumnDataFrame(getfrom, colname='landriversegment')
        return self.singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'landriversegment'],
                                  fromtable=getfrom, toname='lrsegid')

    def names_from_ids(self, lrsegids=None):
        lrsegids = self.forceToSingleColumnDataFrame(lrsegids, colname='landriversegment')
        return self.singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'landriversegment'],
                                  fromtable=lrsegids, toname='landriversegment')

    def lrsegids_from(self, lrsegnames=None, countystatestrs=None, countyid=None):
        kwargs = (lrsegnames, countystatestrs, countyid)
        kwargsNoDataFrames = [True if isinstance(x, pd.DataFrame) else x for x in kwargs]
        if self.checkOnlyOne(kwargsNoDataFrames) is False:
            raise ValueError('One and only one keyword argument must be specified')

        if lrsegnames is not None:
            return self.__lrsegids_from_lrsegnames(getfrom=lrsegnames)
        elif countystatestrs is not None:
            return self.__lrsegids_from_countystatestrs(getfrom=countystatestrs)
        elif countyid is not None:
            return self.__lrsegids_from_countyid(getfrom=countyid)
        else:
            raise ValueError('unrecognized input')