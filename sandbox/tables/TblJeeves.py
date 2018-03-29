import os
import pickle
import numpy as np
import pandas as pd
from tqdm import tqdm

from sandbox.sqltables.source_data import SourceData
from sandbox.tables.TblLoader_fromSql import TblLoaderFromSQL
from sandbox.tables.QrySource_fromSql import QrySourceFromSQL
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


class TblJeeves:
    def __init__(self):
        """Wrapper for table queries. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.source = self.loadSourceFromSQL()
        #self.source = QrySourceFromSQL(tables=self.tables)

    def loadSourceFromSQL(self):
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

    def countyid_from_areanames(self, areanames=None):
        TblCounty = self.source.TblCounty  # get relevant source data

        areas = pd.Series([x.split(', ') for x in areanames])  # split ('County, StateAbbrev')
        mask = pd.DataFrame(areas.values.tolist(), index=areas.index,
                            columns=['countyname', 'stateabbreviation'])

        countytblsubset = TblCounty.loc[:, ['countyid', 'countyname', 'stateid', 'stateabbreviation', 'fips']]\
                                   .merge(mask, how='inner')

        return countytblsubset.countyid

    def lrsegs_from_geography(self, scale='', areanames=None):
        pass
        # return self.source.get_lrseg_table(scale=scale, areanames=areanames)

    def agencies_from_lrsegs(self, lrsegs=None):
        pass
        # return self.source.get_agencies_in_lrsegs(lrsegs=lrsegs)

    def get_all_sector_names(self):
        pass
        # return self.source.get_all_sector_names()