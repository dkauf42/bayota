import os
import pickle

from tables.TblSourceData import SourceData
from tables.TblBaseCondition import BaseCondition
from tables.TblPreBmpLoadSourceNatural import TblPreBmpLoadSourceNatural
from tables.TblPreBmpLoadSourceDeveloped import TblPreBmpLoadSourceDeveloped
from tables.TblPreBmpLoadSourceAgriculture import TblPreBmpLoadSourceAgriculture
from tables.TblManureTonsProduced import ManureTonsProduced
from tables.TblSepticSystems import TblSepticSystems


class TblLoader:
    def __init__(self):
        """Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.
        """
        self.srcdata = None
        self.basecond = None
        self.lsnatural = None
        self.lsdeveloped = None
        self.lsagriculture = None
        self.manuretons = None
        self.septicsystems = None

        self.load_source_and_base_files()

    def load_source_and_base_files(self):
        # BMP Source Data from the Excel Spreadsheet
        self.srcdata = self.load_or_generate(savename='cast_opt_src.obj', cls=SourceData)

        # Base Condition Data from the Excel Spreadsheet (which has Load Source acreage per LRS)
        self.basecond = self.load_or_generate(savename='cast_opt_base.obj',
                                              cls=BaseCondition)

        # PreBmpLoadSourceNatural from the Excel Spreadsheet
        self.lsnatural = self.load_or_generate(savename='cast_opt_loadsourcenatural.obj',
                                               cls=TblPreBmpLoadSourceNatural)

        # PreBmpLoadSourceDeveloped from the Excel Spreadsheet
        self.lsdeveloped = self.load_or_generate(savename='cast_opt_loadsourcedeveloped.obj',
                                                 cls=TblPreBmpLoadSourceDeveloped)

        # PreBmpLoadSourceAgriculture from the Excel Spreadsheet
        self.lsagriculture = self.load_or_generate(savename='cast_opt_loadsourceagriculture.obj',
                                                   cls=TblPreBmpLoadSourceAgriculture)

        # ManureTonsProduced from the Excel Spreadsheet
        self.manuretons = self.load_or_generate(savename='cast_opt_manuretonsproduced.obj',
                                                cls=ManureTonsProduced)

        # SepticSystems from the Excel Spreadsheet
        self.septicsystems = self.load_or_generate(savename='cast_opt_septicsystems.obj',
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
