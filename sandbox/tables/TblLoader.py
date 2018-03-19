import os
import pickle
from pandas import Series

from sandbox.tables.TblSourceData import SourceData
from sandbox.tables.TblBaseCondition import BaseCondition
from sandbox.tables.TblPreBmpLoadSourceNatural import TblPreBmpLoadSourceNatural
from sandbox.tables.TblPreBmpLoadSourceDeveloped import TblPreBmpLoadSourceDeveloped
from sandbox.tables.TblPreBmpLoadSourceAgriculture import TblPreBmpLoadSourceAgriculture
from sandbox.tables.TblManureTonsProduced import ManureTonsProduced
from sandbox.tables.TblSepticSystems import TblSepticSystems
from sandbox.__init__ import get_tempdir


class TblLoader:
    def __init__(self):
        """Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.

        Attributes:
            tempdir (str): location where table objects are written to file to speed up re-runs

        """
        self.tempdir = get_tempdir()

        self.srcdata = None
        self.basecond = None
        self.lsnatural = None
        self.lsdeveloped = None
        self.lsagriculture = None
        self.lsmanure = None
        self.lsseptic = None

        self._load_source_and_base_files()

    def _load_source_and_base_files(self):
        # BMP Source Data from the Excel Spreadsheet
        self.srcdata = self.load_or_generate(savename=self.tempdir + 'cast_opt_src.obj', cls=SourceData)

        # Base Condition Data from the Excel Spreadsheet (which has Load Source acreage per LRS)
        self.basecond = self.load_or_generate(savename=self.tempdir + 'cast_opt_base.obj',
                                              cls=BaseCondition)

        # PreBmpLoadSourceNatural from the Excel Spreadsheet
        self.lsnatural = self.load_or_generate(savename=self.tempdir + 'cast_opt_loadsourcenatural.obj',
                                               cls=TblPreBmpLoadSourceNatural)

        # PreBmpLoadSourceDeveloped from the Excel Spreadsheet
        self.lsdeveloped = self.load_or_generate(savename=self.tempdir + 'cast_opt_loadsourcedeveloped.obj',
                                                 cls=TblPreBmpLoadSourceDeveloped)

        # PreBmpLoadSourceAgriculture from the Excel Spreadsheet
        self.lsagriculture = self.load_or_generate(savename=self.tempdir + 'cast_opt_loadsourceagriculture.obj',
                                                   cls=TblPreBmpLoadSourceAgriculture)

        # ManureTonsProduced from the Excel Spreadsheet
        self.lsmanure = self.load_or_generate(savename=self.tempdir + 'cast_opt_manuretonsproduced.obj',
                                              cls=ManureTonsProduced)

        # SepticSystems from the Excel Spreadsheet
        self.lsseptic = self.load_or_generate(savename=self.tempdir + 'cast_opt_septicsystems.obj',
                                              cls=TblSepticSystems)

    @staticmethod
    def load_or_generate(savename='', cls=None):
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                tableobj = pickle.load(f)
        else:
            tableobj = cls()  # generate data table object if none exists
            with open(savename, 'wb') as f:
                pickle.dump(tableobj, f)

        return tableobj

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

        if isinstance(codes, Series):
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

        if isinstance(names, Series):
            retval = names.replace(dict_agencykeys, inplace=False)
        elif isinstance(names, list):
            retval = list(dict_agencykeys.get(word, word) for word in names)
        else:
            raise TypeError('Unexpected input type for "names" input argument')

        return retval
