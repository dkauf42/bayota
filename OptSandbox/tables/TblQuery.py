from tables.QrySource import QrySource
from tables.QryBase import QryBase


class TblQuery:
    def __init__(self, tables=None):
        """Wrapper for table queries. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.tables = tables
        self.source = QrySource(tables=self.tables)
        self.base = QryBase(tables=self.tables)


