import os
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm

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


class TblLoaderFromSQL:
    def __init__(self):
        """Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.

        Attributes:
            tempdir (str): location where table objects are written to file to speed up re-runs

        """
        self.tempdir = get_tempdir()

        self.load_or_generate_source(savename=self.tempdir + 'SourceData.obj')

    def loadSourceData(self):
        # Source tables are loaded.
        sourcedata = SourceData()
        tbllist = sourcedata.getTblList()
        for tblName in tqdm(tbllist, total=len(tbllist)):
            # for tblName in tbllist:
            # print("loading source:", tblName)
            df = loadDataframe(tblName, get_sqlsourcetabledir())
            sourcedata.addTable(tblName, df)

        return sourcedata

    def load_or_generate_source(self, savename=''):
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                sourceobj = pickle.load(f)
        else:
            print('<%s object does not exist yet. Generating...>' % SourceData.__name__)
            sourceobj = self.loadSourceData()
            #tableobj = cls()  # generate data table object if none exists
            with open(savename, 'wb') as f:
                pickle.dump(sourceobj, f)

        return sourceobj

    def agencytranslate_fromcodes(self, codes):
        """Convert an AgencyCode to its Agency Name

        Args:
            codes (pandas.Series or list): agency code strings

        Example:
            >> .agencytranslate('FWS')
            returns 'US Fish and Wildlife Service'

        """
        df = self.srcdata.agencies
        dict_agencycodekeys = dict(zip(df.AgencyCode, df.Agency))

        if isinstance(codes, pd.Series):
            retval = codes.replace(dict_agencycodekeys, inplace=False)
        elif isinstance(codes, list):
            retval = list(dict_agencycodekeys.get(word, word) for word in codes)
        else:
            raise TypeError('Unexpected input type for "codes" input argument')

        return retval

    def agencytranslate_fromnames(self, names):
        """Convert an Agency Name to its AgencyCode

        Args:
            names (pandas.Series or list): agency names

        Example:
            >> .agencytranslate('Department of Defense')
            returns 'DOD'

        """
        df = self.srcdata.agencies
        dict_agencykeys = dict(zip(df.Agency, df.AgencyCode))

        if isinstance(names, pd.Series):
            retval = names.replace(dict_agencykeys, inplace=False)
        elif isinstance(names, list):
            retval = list(dict_agencykeys.get(word, word) for word in names)
        else:
            raise TypeError('Unexpected input type for "names" input argument')

        return retval
