import pandas as pd
import warnings

from sandbox.util.Jeeves.sourcehooks.sourcehooks import SourceHook


class County(SourceHook):
    def __init__(self, sourcedata=None):
        """ County Methods """
        SourceHook.__init__(self, sourcedata=sourcedata)

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

    def countyid_from_countystatestrs(self, getfrom=None):
        TblCounty = self.source.TblCounty  # get relevant source data

        areas = [x.split(', ') for x in getfrom]  # split ('County, StateAbbrev')
        rowmask = pd.DataFrame(areas, columns=['countyname', 'stateabbreviation'])

        columnmask = ['countyid', 'countyname', 'stateid', 'stateabbreviation', 'fips']
        tblsubset = TblCounty.loc[:, columnmask].merge(rowmask, how='inner')

        return tblsubset.loc[:, ['countyid']]  # pass column name as list so return type is pandas.DataFrame
