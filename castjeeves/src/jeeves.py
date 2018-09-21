import os
import pickle
import numpy as np
import pandas as pd

from . import get_tempdir
from . import get_sqlsourcetabledir
from . import get_sqlmetadatatabledir

from .sqltables.source_data import SourceData
from .sqltables.metadata import Metadata as sqlMetaData

from .sourcehooks.agency import Agency
from .sourcehooks.animal import Animal
from .sourcehooks.bmp import Bmp
from .sourcehooks.county import County
from .sourcehooks.geo import Geo
from .sourcehooks.loadsource import LoadSource
from .sourcehooks.lrseg import Lrseg
from .sourcehooks.meta import Metadata
from .sourcehooks.sector import Sector
from .sourcehooks.translator import Translator


class Jeeves:
    def __init__(self):
        self.source = self.loadInSourceDataFromSQL()
        self.meta = self.loadInMetaDataFromSQL()

        self.agency = Agency(sourcedata=self.source)
        self.animal = Animal(sourcedata=self.source)
        self.bmp = Bmp(sourcedata=self.source)
        self.county = County(sourcedata=self.source)
        self.geo = Geo(sourcedata=self.source)
        self.loadsource = LoadSource(sourcedata=self.source)
        self.lrseg = Lrseg(sourcedata=self.source)
        self.metadata = Metadata(sourcedata=self.source)
        self.sector = Sector(sourcedata=self.source)
        self.translator = Translator(sourcedata=self.source)

    @classmethod
    def loadInSourceDataFromSQL(cls):
        savename = get_tempdir() + 'SourceData.obj'
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


    @classmethod
    def loadInMetaDataFromSQL(cls):
        savename = get_tempdir() + 'MetaData.obj'
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                metadata = pickle.load(f)
        else:
            print('<%s object does not exist yet. Generating...>' % SourceData.__name__)
            # Source tables are loaded.
            metadata = sqlMetaData()
            tbllist = metadata.getTblList()
            for tblName in tbllist:
                # for tblName in tbllist:
                # print("loading source:", tblName)
                df = cls.loadDataframe(tblName, get_sqlmetadatatabledir())
                metadata.addTable(tblName, df)

            with open(savename, 'wb') as f:
                pickle.dump(metadata, f)

        return metadata

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
