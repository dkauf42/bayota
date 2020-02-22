import pandas as pd

from .sourcehooks import SourceHook
# from .agency import Agency
# from .lrseg import Lrseg
# from .sector import Sector


class Animal(SourceHook):
    def __init__(self, sourcedata=None, metadata=None):
        """ Methods for querying CAST data related to Animals """
        SourceHook.__init__(self, sourcedata=sourcedata, metadata=metadata)

        # self.agency = Agency(sourcedata=sourcedata)
        # self.lrseg = Lrseg(sourcedata=sourcedata)
        # self.sector = Sector(sourcedata=sourcedata)

    def manuredrytons_from(self, basecondcountyanimalids=None):
        TblAnimalYearly = self.source.TblAnimalYearly

        # Get which animals are present in the county, agency, loadsources
        columnmask = ['manurelbsperanimaldaily', 'manurelbsperanimalunitdaily', 'baseconditionid', 'countyid', 'animalid']
        tblsubset = TblAnimalYearly.loc[:, columnmask].merge(basecondcountyanimalids, how='inner')

        return tblsubset
