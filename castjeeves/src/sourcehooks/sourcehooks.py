import os
import numpy as np
import pandas as pd
from itertools import product
from itertools import permutations
import warnings


class SourceHook:
    def __init__(self, sourcedata=None, metadata=None):
        """Base Class for source data queries.

        Attributes:
            source (SourceData): The source object contains all of the data tables

        Required Methods:
            all_names()
            all_ids()
            ids_from_names()
            names_from_ids()

        """
        self.source = sourcedata
        self.metadata_tables = metadata

    def all_names(self):
        pass
    def all_ids(self):
        pass
    def ids_from_names(self):
        pass
    def names_from_ids(self):
        pass

    def singleconvert(self, sourcetbl=None, toandfromheaders=None,
                      fromtable=None, toname='',
                      use_order_of_sourcetbl=True):
        sourcetable = getattr(self.source, sourcetbl)

        if use_order_of_sourcetbl:
            tblsubset = sourcetable.loc[:, toandfromheaders].merge(fromtable, how='inner')
        else:
            tblsubset = fromtable.merge(sourcetable.loc[:, toandfromheaders], how='inner')

        return tblsubset.loc[:, [toname]]  # pass column name as list so return type is pandas.DataFrame

    def append_ids_to_table(self, sourcetbl=None, commonheaders_with_append=None, fromtable=None):
        sourcetable = getattr(self.source, sourcetbl)
        tblsubset = sourcetable.loc[:, commonheaders_with_append].merge(fromtable, how='inner')

        return tblsubset

    @staticmethod
    def checkOnlyOne(iterable):
        i = iter(iterable)
        return any(i) and not any(i)

    @staticmethod
    def forceToSingleColumnDataFrame(inputarg, colname=''):
        if not isinstance(inputarg, pd.DataFrame):
            return pd.DataFrame(inputarg, columns=[colname])
        else:
            return inputarg
