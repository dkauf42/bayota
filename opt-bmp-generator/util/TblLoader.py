import os
import pickle

from tables.TblSourceData import SourceData
from tables.TblBaseCondition import BaseCondition
from tables.TblPreBmpLoadSourceNatural import TblPreBmpLoadSourceNatural
from tables.TblPreBmpLoadSourceDeveloped import TblPreBmpLoadSourceDeveloped
from tables.TblPreBmpLoadSourceAgriculture import TblPreBmpLoadSourceAgriculture
from tables.TblManureTonsProduced import ManureTonsProduced
from tables.TblSepticSystems import TblSepticSystems

srcdatadir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/'


class TblLoader:
    def __init__(self):
        """Objects that contain the BMP Source Data and Base Condition Data are loaded or generated.
        """
        self.srcdataobj = None
        self.baseconditionobj = None
        self.tableobjs = {}

        self.load_source_and_base_files()
        pass

    def load_or_generate(self, savename='', tableobjname='', cls=None):
        if os.path.exists(savename):
            with open(savename, 'rb') as f:
                self.tableobjs[tableobjname] = pickle.load(f)
        else:
            self.tableobjs[tableobjname] = cls()  # generate data table object if none exists
            with open(savename, 'wb') as f:
                pickle.dump(self.tableobjs[tableobjname], f)

    def load_source_and_base_files(self):

        # BMP Source Data from the Excel Spreadsheet
        self.load_or_generate(savename='cast_opt_src.obj',
                              tableobjname='srcdataobj',
                              cls=SourceData)

        # Base Condition Data from the Excel Spreadsheet (which has Load Source acreage per LRS)
        self.load_or_generate(savename='cast_opt_base.obj',
                              tableobjname='baseconditionobj',
                              cls=BaseCondition)

        # PreBmpLoadSourceNatural from the Excel Spreadsheet
        self.load_or_generate(savename='cast_opt_loadsourcenatural.obj',
                              tableobjname='loadsourcenaturalobj',
                              cls=TblPreBmpLoadSourceNatural)

        # PreBmpLoadSourceDeveloped from the Excel Spreadsheet
        self.load_or_generate(savename='cast_opt_loadsourcedeveloped.obj',
                              tableobjname='loadsourcedevelopedobj',
                              cls=TblPreBmpLoadSourceDeveloped)

        # PreBmpLoadSourceAgriculture from the Excel Spreadsheet
        self.load_or_generate(savename='cast_opt_loadsourceagriculture.obj',
                              tableobjname='loadsourceagricultureobj',
                              cls=TblPreBmpLoadSourceAgriculture)

        # ManureTonsProduced from the Excel Spreadsheet
        self.load_or_generate(savename='cast_opt_manuretonsproduced.obj',
                              tableobjname='manuretonsproducedobj',
                              cls=ManureTonsProduced)

        # SepticSystems from the Excel Spreadsheet
        self.load_or_generate(savename='cast_opt_septicsystems.obj',
                              tableobjname='septicsystemsobj',
                              cls=TblSepticSystems)

        # # BMP Source Data from the Excel Spreadsheet
        # picklename = 'cast_opt_src.obj'
        # if os.path.exists(picklename):
        #     with open(picklename, 'rb') as f:
        #         self.srcdataobj = pickle.load(f)
        # else:
        #     self.srcdataobj = SourceData()  # generate source data object if none exists
        #     with open(picklename, 'wb') as f:
        #         pickle.dump(self.srcdataobj, f)
        #
        # # Base Condition Data (which has Load Source acreage per LRS)
        # picklename = 'cast_opt_base.obj'
        # if os.path.exists(picklename):
        #     with open(picklename, 'rb') as f:
        #         self.baseconditionobj = pickle.load(f)
        # else:
        #     self.baseconditionobj = BaseCondition()  # generate base condition object if none exists
        #     with open(picklename, 'wb') as f:
        #         pickle.dump(self.baseconditionobj, f)
        # print('<Loaded> BMP Source Data and Base Condition Data.')
        #
        # # Base Condition Data (which has Load Source acreage per LRS)
        # picklename = 'cast_opt_base.obj'
        # if os.path.exists(picklename):
        #     with open(picklename, 'rb') as f:
        #         self.baseconditionobj = pickle.load(f)
        # else:
        #     self.baseconditionobj = BaseCondition()  # generate base condition object if none exists
        #     with open(picklename, 'wb') as f:
        #         pickle.dump(self.baseconditionobj, f)
        # print('<Loaded> BMP Source Data and Base Condition Data.')
        #
        # # Base Condition Data (which has Load Source acreage per LRS)
        # picklename = 'cast_opt_base.obj'
        # if os.path.exists(picklename):
        #     with open(picklename, 'rb') as f:
        #         self.baseconditionobj = pickle.load(f)
        # else:
        #     self.baseconditionobj = BaseCondition()  # generate base condition object if none exists
        #     with open(picklename, 'wb') as f:
        #         pickle.dump(self.baseconditionobj, f)
        # print('<Loaded> BMP Source Data and Base Condition Data.')