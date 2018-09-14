import os
import pickle
import numpy as np
import pandas as pd

from . import get_tempdir
from . import get_sqlsourcetabledir

from .sqltables.source_data import SourceData

from .sourcehooks.agency import Agency
from .sourcehooks.animal import Animal
from .sourcehooks.bmp import Bmp
from .sourcehooks.county import County
from .sourcehooks.geo import Geo
from .sourcehooks.loadsource import LoadSource
from .sourcehooks.lrseg import Lrseg
from .sourcehooks.metadata import Metadata
from .sourcehooks.sector import Sector
from .sourcehooks.translator import Translator


class Jeeves:
    def __init__(self):
        source = self.loadInSourceDataFromSQL()

        self.agency = Agency(sourcedata=source)
        self.animal = Animal(sourcedata=source)
        self.bmp = Bmp(sourcedata=source)
        self.county = County(sourcedata=source)
        self.geo = Geo(sourcedata=source)
        self.loadsource = LoadSource(sourcedata=source)
        self.lrseg = Lrseg(sourcedata=source)
        self.metadata = Metadata(sourcedata=source)
        self.sector = Sector(sourcedata=source)
        self.translator = Translator(sourcedata=source)

    @classmethod
    def loadInSourceDataFromSQL(cls):
        savename = get_tempdir() + 'SourceData.obj'
        print(get_tempdir())
        print(os.listdir(get_tempdir()))
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                sourcedata = pickle.load(f)
        else:
            print('<%s object does not exist yet. Generating...>' % SourceData.__name__)
            # Source tables are loaded.
            sourcedata = SourceData()
            tbllist = sourcedata.getTblList()
            for tblName in tbllist:
                # for tblName in tbllist:
                # print("loading source:", tblName)
                df = cls.loadDataframe(tblName, get_sqlsourcetabledir())
                sourcedata.addTable(tblName, df)

            with open(savename, 'wb') as f:
                pickle.dump(sourcedata, f)

        return sourcedata

    @staticmethod
    def loadDataframe(tblName, loc):
        dtype_dict = {}
        if tblName == "ImpBmpSubmittedManureTransport":
            dtype_dict["fipsfrom"] = np.str

        fileLocation = os.path.join(loc, tblName + ".csv")

        df = pd.read_csv(fileLocation, dtype=dtype_dict, encoding="utf-8")

        # Added by DEKAUFMAN to read csv in chunks instead of all at once
        # tp = pd.read_csv(fileLocation, header=None, encoding="utf-8", chunksize=500000)
        # df = pd.concat(tp, ignore_index=True)

        df = df.rename(columns={column: column.lower() for column in df.columns})

        if tblName == "TblBmpGroup":
            df["ruleset"] = df["ruleset"].astype(str).str.lower()
        return df
