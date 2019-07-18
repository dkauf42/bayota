import pandas as pd
import warnings

from .sourcehooks import SourceHook
from .lrseg import Lrseg


class County(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ County Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)

    def all_names(self, astype=pd.Series):
        TblCounty = self.source.TblCounty  # get relevant source data
        name_series = TblCounty.loc[:, 'countyname']
        return self.type_convert(name_series, astype)

    def all_ids(self):
        pass

    def ids_from_names(self):
        pass

    def names_from_ids(self, countyids=None):
        return self._map_using_sourcetbl(countyids, tbl='TblCounty',
                                         fromcol='countyid', tocol='countyname')

    def validate_countystatestrs(self, countystatestrs=None):
        """

        Args:
            countystatestrs (list of str):

        Returns:
            pd.DataFrame

        """
        try:
            areas = [x.split(', ') for x in countystatestrs]  # split ('County, StateAbbrev')
            df = pd.DataFrame(areas, columns=['countyname', 'stateabbreviation'])
            df['stateabbreviation'] = df['stateabbreviation'].str.lower()
            return df
        except (AssertionError, ValueError) as e:
            raise Exception('** Invalid County Input **\n'
                            '   %s is invalid'
                            '   -- Must be list of comma-separated strings'
                            '   -- e.g. [\'Adams, PA\', \'Hardy, WV\']'
                            % countystatestrs).with_traceback(e.__traceback__)

    def countyid_from_countystatestrs(self, getfrom=None, append=False):
        TblCounty = self.source.TblCounty  # get relevant source data

        rowmask = self.validate_countystatestrs(getfrom)

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

