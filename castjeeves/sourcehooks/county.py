import pandas as pd
import warnings

from .sourcehooks import SourceHook
from .lrseg import Lrseg


class County(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Methods for querying CAST data related to County geographies """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        self.lrseg = Lrseg(sourcedata=sourcedata, metadata=metadata)

    def all_names(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblCounty', col='countyname', astype=astype)

    def all_ids(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblCounty', col='countyid', astype=astype)

    def ids_from_names(self, ids):
        raise LookupError('ids_from_names() method is not available for counties, '
                          'because they must be specified using both a county name and a state abbreviation')

    def names_from_ids(self, countyids=None):
        return self._map_using_sourcetbl(countyids, tbl='TblCounty',
                                         fromcol='countyid', tocol='countyname')

    def validate_countystatestrs(self, countystatestrs=None) -> pd.DataFrame:
        """

        Args:
            countystatestrs (list of str):

        Returns:
            pd.DataFrame

        """
        try:
            # split ('County, StateAbbrev')
            areas = [x.split(', ') for x in countystatestrs]
            df = pd.DataFrame(areas, columns=['countyname', 'stateabbreviation'])
            df['stateabbreviation'] = df['stateabbreviation'].str.lower()
            return df
        except (AssertionError, ValueError) as e:
            raise Exception('** Invalid County Input **\n'
                            '   %s is invalid'
                            '   -- Must be list of comma-separated strings'
                            '   -- e.g. [\'Adams, PA\', \'Hardy, WV\']'
                            % countystatestrs).with_traceback(e.__traceback__)

    def countyid_from_countystatestrs(self, getfrom=None, astype=None, append=False):
        TblCounty = self.source.TblCounty  # get relevant source data

        rowmask = self.validate_countystatestrs(getfrom)
        rowmask['countyname'] = rowmask['countyname'].str.lower()
        columnmask = ['countyid', 'countyname', 'stateabbreviation']
        subtbl = TblCounty.loc[:, columnmask]
        subtbl['countyname'] = subtbl['countyname'].str.lower()
        countyids = subtbl.merge(rowmask, how='inner').loc[:, 'countyid']

        if isinstance(getfrom, list):
            countyids = countyids.tolist()
        elif isinstance(getfrom, pd.Series):
            pass
        else:
            raise TypeError(f"unexpected type <{type(getfrom)}>")

        if astype:
            return self.type_convert(orig=countyids, astype=astype)
        else:
            return countyids

    def add_lrsegs_to_counties(self, countystatestrs=None):
        countyids = self.countyid_from_countystatestrs(getfrom=countystatestrs)
        strnospaces = [''.join(x.split(', ')).replace(" ", "") for x in countystatestrs]

        df = pd.DataFrame(countyids, columns=['countyid'])
        df['countystatestr'] = strnospaces

        return self.lrseg.append_lrsegs_to_counties(tablewithcountyids=df)

