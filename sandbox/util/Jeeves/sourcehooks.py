import os
import pickle
import numpy as np
import pandas as pd
from itertools import product
from itertools import permutations
from tqdm import tqdm
import warnings

from sandbox.sqltables.source_data import SourceData
from sandbox.__init__ import get_tempdir
from sandbox.__init__ import get_sqlsourcetabledir


def loadDataframe(tblName, loc):
    dtype_dict = {}
    if tblName == "ImpBmpSubmittedManureTransport":
        dtype_dict["fipsfrom"] = np.str

    fileLocation = os.path.join(loc, tblName + ".csv")

    df = pd.read_csv(fileLocation, dtype=dtype_dict, encoding="utf-8")

    # Added by DEKAUFMAN to read csv in chunks instead of all at once
    #tp = pd.read_csv(fileLocation, header=None, encoding="utf-8", chunksize=500000)
    #df = pd.concat(tp, ignore_index=True)

    df = df.rename(columns={column: column.lower() for column in df.columns})

    if tblName == "TblBmpGroup":
        df["ruleset"] = df["ruleset"].astype(str).str.lower()
    return df


class SourceHook:
    def __init__(self):
        """Base Class for source data queries.

        Attributes:
            source (SourceData): The source object contains all of the data tables

        Required Methods:
            all_names()
            all_ids()
            ids_from_names()
            names_from_ids()

        """
        self.source = self.loadInSourceDataFromSQL()

    def all_names(self):
        pass
    def all_ids(self):
        pass
    def ids_from_names(self):
        pass
    def names_from_ids(self):
        pass

    def loadInSourceDataFromSQL(self):
        savename = get_tempdir() + 'SourceData.obj'

        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                sourcedata = pickle.load(f)
        else:
            print('<%s object does not exist yet. Generating...>' % SourceData.__name__)
            # Source tables are loaded.
            sourcedata = SourceData()
            tbllist = sourcedata.getTblList()
            for tblName in tqdm(tbllist, total=len(tbllist)):
                # for tblName in tbllist:
                # print("loading source:", tblName)
                df = loadDataframe(tblName, get_sqlsourcetabledir())
                sourcedata.addTable(tblName, df)

            with open(savename, 'wb') as f:
                pickle.dump(sourcedata, f)

        return sourcedata

    def singleconvert(self, sourcetbl=None, toandfromheaders=None, fromtable=None, toname=''):
        sourcetable = getattr(self.source, sourcetbl)
        tblsubset = sourcetable.loc[:, toandfromheaders].merge(fromtable, how='inner')

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
