import pandas as pd
import warnings

from .sourcehooks import SourceHook
from .lrseg import Lrseg


class County(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ County Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)

    def all_names(self):
        pass

    def all_ids(self):
        pass

    def ids_from_names(self):
        pass

    def names_from_ids(self, countyids=None):
        countyids = self.forceToSingleColumnDataFrame(countyids, colname='countyid')
        return self.singleconvert(sourcetbl='TblCounty', toandfromheaders=['countyid', 'countyname'],
                                  fromtable=countyids, toname='countyname')

    def countyid_from_countystatestrs(self, getfrom=None, append=False):
        TblCounty = self.source.TblCounty  # get relevant source data

        areas = [x.split(', ') for x in getfrom]  # split ('County, StateAbbrev')
        rowmask = pd.DataFrame(areas, columns=['countyname', 'stateabbreviation'])

        columnmask = ['countyid', 'countyname', 'stateid', 'stateabbreviation', 'fips']
        tblsubset = TblCounty.loc[:, columnmask].merge(rowmask, how='inner')

        if append:
            return tblsubset.loc[:, ['countyname', 'countyid']]
        else:
            return tblsubset.loc[:, ['countyid']]  # pass column name as list so return type is pandas.DataFrame

    def add_lrsegs_to_counties(self, countystatestrs=None):
        countyids = self.countyid_from_countystatestrs(getfrom=countystatestrs, append=True)

        strnospaces = [''.join(x.split(', ')).replace(" ", "") for x in countystatestrs]
        countyids['countystatestrs'] = strnospaces

        tblsubset = self.lrseg.append_lrsegs_to_counties(tablewithcountyids=countyids)

        return tblsubset

