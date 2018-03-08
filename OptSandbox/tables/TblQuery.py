from util.TblLoader import TblLoader
from tables.QrySource import QrySource
from tables.QryBase import QryBase
from tables.QryLoadSources import QryLoadSources


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


