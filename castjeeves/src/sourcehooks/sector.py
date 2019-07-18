from .sourcehooks import SourceHook


class Sector(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Sector Methods """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

    # Sector Methods
    def all_names(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, 'sector']

    def all_ids(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, ['sectorid']]

    def ids_from_names(self, names=None):
        return self._map_using_sourcetbl(names, tbl='TblSector',
                                         fromcol='sector', tocol='sectorid')

    def sectors_from_loadsourceshortname(self, loadsourceshortnames):
        names = self.forceToSingleColumnDataFrame(loadsourceshortnames, colname='loadsourceshortname')
        sectorids = self.singleconvert(sourcetbl='TblLoadSource', toandfromheaders=['loadsourceshortname', 'sectorid'],
                           fromtable=names, toname='sectorid', use_order_of_sourcetbl=False)
        return self.singleconvert(sourcetbl='TblSector', toandfromheaders=['sectorid', 'sector'],
                                  fromtable=sectorids, toname='sector', use_order_of_sourcetbl=False)
