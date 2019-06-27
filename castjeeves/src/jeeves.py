import os
import pickle
import numpy as np
import pandas as pd

from bayota_settings.base import get_source_pickles_dir
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
from .sourcehooks.meta import Meta
from .sourcehooks.sector import Sector
from .sourcehooks.translator import Translator

import logging
logger = logging.getLogger(__name__)


class Jeeves:
    """ This class provides a framework for querying the CAST source data files.

    Access to parts of the source data is split among hopefully-intuitive groupings.

    Attributes:
        agency ():
        animal ():
        bmp ():
        county ():
        geo ():
        loadsource ():
        lrseg ():
        sector ():

        meta ():
        translator ():
        source (str): Description of `attr1`.
        metadata_tables (:obj:`int`, optional): Description of `attr2`.
    """
    def __init__(self):
        self.source = self.loadInSourceDataFromSQL()
        self.metadata_tables = self.loadInMetaDataFromSQL()

        self.agency = Agency(sourcedata=self.source)
        self.animal = Animal(sourcedata=self.source)
        self.bmp = Bmp(sourcedata=self.source)
        self.county = County(sourcedata=self.source)
        self.geo = Geo(sourcedata=self.source)
        self.loadsource = LoadSource(sourcedata=self.source)
        self.lrseg = Lrseg(sourcedata=self.source)
        self.meta = Meta(sourcedata=self.source, metadata=self.metadata_tables)
        self.sector = Sector(sourcedata=self.source)
        self.translator = Translator(sourcedata=self.source)

    @classmethod
    def loadInSourceDataFromSQL(cls):
        """Loads in the source data from a pickle object,
        or if it doesn't exist, makes a pickle file from the csv files.

        Returns:
            a SourceData object
        """
        savename = os.path.join(get_source_pickles_dir(), 'SourceData.obj')
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                sourcedata = pickle.load(f)
        else:
            logger.info('<%s object does not exist yet. Generating...>' % SourceData.__name__)
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
        """Loads in the metadata from a pickle object,
        or if it doesn't exist, makes a pickle file from the csv files.

        Returns:
            a sqlMetaData object
        """
        savename = os.path.join(get_source_pickles_dir(), 'MetaData.obj')
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                metadata = pickle.load(f)
        else:
            logger.info('<%s object does not exist yet. Generating...>' % sqlMetaData.__name__)
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
        """ """
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
