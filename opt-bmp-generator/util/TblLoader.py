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
        self.lsmanure = None
        self.lsseptic = None

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
        self.lsmanure = self.load_or_generate(savename='cast_opt_manuretonsproduced.obj',
                                              cls=ManureTonsProduced)

        # SepticSystems from the Excel Spreadsheet
        self.lsseptic = self.load_or_generate(savename='cast_opt_septicsystems.obj',
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

    def agencytranslate(self, nameorcode):
        """Convert an Agency Name to its AgencyCode or vice versa

        Examples:
            >> .agencytranslate('Department of Defense')
            returns 'DOD'

            >> .agencytranslate('FWS')
            returns 'US Fish and Wildlife Service'
        """
        df = self.srcdata.agencies
        boolseries1 = df['Agency'] == nameorcode
        boolseries2 = df['AgencyCode'] == nameorcode
        if any(boolseries1) & any(boolseries2):
            raise ValueError('agency <%s> cannot be both an Agency "Name" and "Code"' % nameorcode)

        if any(boolseries1):
            return df['AgencyCode'][boolseries1].to_string()
        elif any(boolseries2):
            return df['Agency'][boolseries2].to_string()
        else:
            raise ValueError('agency <%s> cannot be found' % nameorcode)
