import pandas as pd
import warnings

from sandbox.util.jeeves.sourcehooks.sourcehooks import SourceHook


class Lrseg(SourceHook):
    def __init__(self, sourcedata=None):
        """ Geography Methods """
        SourceHook.__init__(self, sourcedata=sourcedata)

    def all_names(self):
        pass

    def all_ids(self):
        pass

    def ids_from_names(self, names=None):
        names = self.forceToSingleColumnDataFrame(names, colname='landriversegment')
        return self.singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'landriversegment'],
                                  fromtable=names, toname='lrsegid')

    def names_from_ids(self, ids=None):
        ids = self.forceToSingleColumnDataFrame(ids, colname='landriversegment')
        return self.singleconvert(sourcetbl='TblLandRiverSegment', toandfromheaders=['lrsegid', 'landriversegment'],
                                  fromtable=ids, toname='landriversegment')

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
