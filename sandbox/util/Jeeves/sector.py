from sandbox.util.Jeeves.sourcehooks import SourceHook


class Sector(SourceHook):
    def __init__(self):
        """ Sector Methods """
        SourceHook.__init__(self)

    # Sector Methods
    def sectorids_from(self, sectornames=None):
        sectornames = self.forceToSingleColumnDataFrame(sectornames, colname='sector')
        return self.singleconvert(sourcetbl='TblSector', toandfromheaders=['sector', 'sectorid'],
                                  fromtable=sectornames, toname='sectorid')

    def all_sector_names(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, 'sector']

    def all_sectorids(self):
        TblSector = self.source.TblSector  # get relevant source data
        return TblSector.loc[:, ['sectorid']]