import pandas as pd
from .sourcehooks import SourceHook


class Sector(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Methods for querying CAST data related to Sectors (e.g. Agriculture, Developed, Natural) """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

    # Sector Methods
    def all_names(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblSector', col='sector', astype=astype)

    def all_ids(self, astype=pd.Series):
        return self.grab_sourcetbl_column(tbl='TblSector', col='sectorid', astype=astype)

    def ids_from_names(self, names=None):
        return self._map_using_sourcetbl(names, tbl='TblSector',
                                         fromcol='sector', tocol='sectorid')

    def sectors_from_loadsourceshortname(self, loadsourceshortnames):
        names = self.forceToSingleColumnDataFrame(loadsourceshortnames, colname='loadsourceshortname')
        sectorids = self.singleconvert(sourcetbl='TblLoadSource', toandfromheaders=['loadsourceshortname', 'sectorid'],
                           fromtable=names, toname='sectorid', use_order_of_sourcetbl=False)
        return self.singleconvert(sourcetbl='TblSector', toandfromheaders=['sectorid', 'sector'],
                                  fromtable=sectorids, toname='sector', use_order_of_sourcetbl=False)
