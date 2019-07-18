import os
import numpy as np
import pandas as pd
from itertools import product
from itertools import permutations
import warnings
from typing import List


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

        self._method_dict_for_mapping_type = {list: self._map_LIST_using_sourcetbl,
                                              pd.DataFrame: self._map_DATAFRAME_using_sourcetbl,
                                              pd.Series: self._map_SERIES_using_sourcetbl}

    def type_convert(self, orig, astype):
        if isinstance(orig, pd.Series):
            """ Series """
            if isinstance(astype, str):
                if astype.lower() == 'series':
                    return orig
                elif astype.lower() == 'list':
                    return orig.tolist()
                else:
                    raise TypeError(f"unexpected astype value: <{astype}>")
            else:
                if astype == pd.Series:
                    return orig
                elif astype == list:
                    return orig.tolist()
                else:
                    raise TypeError(f"unexpected astype value: <{astype}>")


    def all_names(self):
        pass
    def all_ids(self):
        pass
    def names_from_ids(self):
        pass
    def ids_from_names(self):
        pass

    def _map_using_multiple_sourcetbls(self, values,
                                       tbls: List[str],
                                       column_sequence: List[str]):
        """

        Args:
            values:
            tbls:
            column_sequence:

        Note:
            len(tbls) must be one less than len(column_sequence)

        Returns:

        Example:
            _map_using_multiple_sourcetbls(
                                           tbls=['TblLandRiverSegmentAgency', 'TblAgency'],
                                           column_sequence=['lrsegid', 'agencyid', 'agencycode']
                                           )

        """
        assert len(column_sequence) == (len(tbls) + 1)

        newvalues = values.copy()
        for i, t in enumerate(tbls):
            sourcetable = getattr(self.source, t)
            newvalues = self._method_dict_for_mapping_type[type(values)](newvalues, sourcetable,
                                                                         fromcol=column_sequence[i],
                                                                         tocol=column_sequence[i+1])

        return newvalues

    def _map_using_sourcetbl(self, values,
                             tbl: str,
                             tocol: str,
                             fromcol: str,
                             todict=False,
                             flatten_to_set=False):
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

        return self._method_dict_for_mapping_type[type(values)](values, sourcetable,
                                                                tocol, fromcol,
                                                                todict=todict, flatten_to_set=flatten_to_set)

    @staticmethod
    def _map_LIST_using_sourcetbl(vals: list,
                                  sourcetable: pd.DataFrame,
                                  tocol: str,
                                  fromcol: str,
                                  todict=False,
                                  flatten_to_set=False):
        """ Return a list of values that have been translated using two columns in a source table """
        if not isinstance(vals, list):
            raise TypeError(f"unexpected type <{type(vals)}>")
        if todict and flatten_to_set:
            raise ValueError(f"todict and flatten_to_set arguments are mutually exclusive; "
                             f"only one can be set to True")

        translate_series = pd.Series(sourcetable[tocol].values, index=sourcetable[fromcol])

        if any(translate_series.index.duplicated()) & (not todict) & (not flatten_to_set):
            raise ValueError('duplicate values in the tocol will be dropped when translating a list! '
                             'try setting todict=True or flatten=True, '
                             'or using a Series or DataFrame instead of a list')

        if todict:
            df = sourcetable.loc[:, [fromcol, tocol]]
            my_series = df.groupby(fromcol)[tocol].apply(list)
            return my_series.loc[vals].to_dict()
        elif flatten_to_set:
            df = sourcetable.loc[:, [fromcol, tocol]]
            my_series = df.groupby(fromcol)[tocol].apply(list)
            return set([item for sublist in my_series.loc[vals] for item in sublist])
        else:
            translate_dict = translate_series.to_dict()
            return [translate_dict[v] for v in vals]

    @staticmethod
    def _map_DATAFRAME_using_sourcetbl(vals: pd.DataFrame,
                                       sourcetable: pd.DataFrame,
                                       tocol: str,
                                       fromcol: str,
                                       todict=False,
                                       flatten_to_set=False):
        """ Return a DataFrame of values that have been translated using two columns in a source table """
        if not isinstance(vals, pd.DataFrame):
            raise TypeError(f"unexpected type <{type(vals)}>")

        my_table = sourcetable.loc[:, [tocol, fromcol]]

        if todict:
            my_series = my_table.groupby(fromcol)[tocol].apply(list)
            return my_series.loc[vals[fromcol]].to_dict()
        elif flatten_to_set:
            my_series = my_table.groupby(fromcol)[tocol].apply(list)
            return set([item for sublist in my_series.loc[vals[fromcol]] for item in sublist])
        else:
            return my_table.merge(vals, how='inner').loc[:, [tocol]]  # pass column name as list so return type is pandas.DataFrame

    @staticmethod
    def _map_SERIES_using_sourcetbl(vals: pd.Series,
                                    sourcetable: pd.DataFrame,
                                    tocol: str,
                                    fromcol: str,
                                    todict=False,
                                    flatten_to_set=False):
        """ Return a Series of values that have been translated using two columns in a source table """
        if not isinstance(vals, pd.Series):
            raise TypeError(f"unexpected type <{type(vals)}>")

        if todict:
            df = sourcetable.loc[:, [fromcol, tocol]]
            my_series = df.groupby(fromcol)[tocol].apply(list)
            return my_series.loc[vals].to_dict()
        elif flatten_to_set:
            df = sourcetable.loc[:, [fromcol, tocol]]
            my_series = df.groupby(fromcol)[tocol].apply(list)
            return set([item for sublist in my_series.loc[vals] for item in sublist])
        else:
            my_series = pd.Series(sourcetable[tocol].values, index=sourcetable[fromcol])
            return vals.map(my_series.to_dict())

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

    def append_column_to_table(self, df_to_append_to, sourcetbl,
                               commoncol, appendcol):
        sourcetable = getattr(self.source, sourcetbl)

        def add_to_list(baselist, colname):
            """ add colname values to list, according to its type """
            if isinstance(colname, str):
                baselist.append(colname)
            elif isinstance(colname, list):
                baselist.extend(colname)
            else:
                raise ValueError(f'unexpected type for {commoncol}')

        includecols = []
        add_to_list(includecols, commoncol)
        add_to_list(includecols, appendcol)

        tblsubset = sourcetable.loc[:, includecols].merge(df_to_append_to, how='inner')

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
