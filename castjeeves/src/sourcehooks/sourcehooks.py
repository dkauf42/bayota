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

        self.id_from_names_map = {list: self._map_LIST_using_sourcetbl,
                                  pd.DataFrame: self._map_DATAFRAME_using_sourcetbl,
                                  pd.Series: self._map_SERIES_using_sourcetbl}

    def all_names(self):
        pass
    def all_ids(self):
        pass

    def _map_using_sourcetbl(self, values, tbl, tocol, fromcol):
        """ Convert values in 's' using a mapping based on the correspondences in the Source table 'tbl'

        This is the main method that will call a type-specific submethod

        Args:
            values (list, pd.DataFrame, or pd.Series): the values to be converted
            tbl (str): name of the source table that will be used for the conversion
            tocol (str): name of the dataframe column that has values to convert TO
            fromcol (str): name of the dataframe column that has values to convert FROM

        Returns:
            a collection that matches the input type and is the same length as the input
        """
        sourcetable = getattr(self.source, tbl)

        return self.id_from_names_map[type(values)](values, sourcetable, tocol, fromcol)

    @staticmethod
    def _map_LIST_using_sourcetbl(values, tbl, tocol, fromcol) -> list:
        """ Return a list of ids, if values argument is a list """
        translate_dict = pd.Series(tbl[tocol].values, index=tbl[fromcol]).to_dict()
        return [translate_dict[v] for v in values]

    @staticmethod
    def _map_DATAFRAME_using_sourcetbl(values, tbl, tocol, fromcol) -> pd.DataFrame:
        """ Return a DataFrame of ids, if values argument is a DataFrame """
        tblsubset = tbl.loc[:, [tocol, fromcol]].merge(values, how='inner')
        return tblsubset.loc[:, [tocol]]  # pass column name as list so return type is pandas.DataFrame

    @staticmethod
    def _map_SERIES_using_sourcetbl(values, tbl, tocol, fromcol) -> pd.Series:
        """ Return a Series of ids, if values argument is a Series """
        translate_dict = pd.Series(tbl[tocol].values, index=tbl[fromcol]).to_dict()
        return values.map(translate_dict)

    def names_from_ids(self):
        pass

    def singleconvert(self, sourcetbl=None, toandfromheaders=None,
                      fromtable=None, toname='',
                      use_order_of_sourcetbl=True):
        sourcetable = getattr(self.source, sourcetbl)

        if use_order_of_sourcetbl:
            tblsubset = sourcetable.loc[:, toandfromheaders].merge(fromtable, how='inner')
        else:
            # TODO: Instead of a "left" merge (which only keeps left keys), this really should be an "inner" merge (which only keeps shared keys) that still retains left table order of keys.
            tblsubset = fromtable.merge(sourcetable.loc[:, toandfromheaders], how='left', sort=False)

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
