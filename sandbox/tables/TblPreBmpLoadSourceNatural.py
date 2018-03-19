from sandbox.tables.ExcelDataTable import ExcelDataTable
from sandbox.__init__ import get_datadir

reportsdir = get_datadir()


class TblPreBmpLoadSourceNatural(ExcelDataTable):
    def __init__(self, filename='2016 Progress V8 - COPY_PreBmpLoadSourceNatural.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['PreBmpLoadSourceNatural'])

        # Data from excel sheets are saved to class attributes.
        self.PreBmpLoadSourceNatural = self.data['PreBmpLoadSourceNatural']
