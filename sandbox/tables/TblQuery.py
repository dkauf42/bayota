from sandbox.tables.TblLoader import TblLoader
from sandbox.tables.QrySource import QrySource
from sandbox.tables.QryBase import QryBase
from sandbox.tables.QryLoadSources import QryLoadSources


class TblQuery:
    def __init__(self):
        """Wrapper for table queries. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """

        self.tables = TblLoader()
        self.source = QrySource(tables=self.tables)
        self.base = QryBase(tables=self.tables)
        self.loadsources = QryLoadSources(tables=self.tables)

    def lrsegs_from_geography(self, scale='', areanames=None):
        return self.source.get_lrseg_table(scale=scale, areanames=areanames)

    def agencies_from_lrsegs(self, lrsegs=None):
        return self.base.get_agencies_in_lrsegs(lrsegs=lrsegs)



