from sandbox.util.Jeeves.sourcehooks import SourceHook


class Sector(SourceHook):
    def __init__(self):
        """ Sector Methods """
        SourceHook.__init__(self)

    # Sector Methods
    def all_names(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, 'sector']

    def all_ids(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, ['sectorid']]

    def ids_from_names(self, names=None):
        names = self.forceToSingleColumnDataFrame(names, colname='sector')
        return self.singleconvert(sourcetbl='TblSector', toandfromheaders=['sector', 'sectorid'],
                                  fromtable=names, toname='sectorid')
