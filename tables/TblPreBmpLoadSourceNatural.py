from tables.ExcelDataTable import ExcelDataTable
from OptSandbox.__init__ import get_data

reportsdir = get_data()


class TblPreBmpLoadSourceNatural(ExcelDataTable):
    def __init__(self, filename='2016 Progress V8 - COPY_PreBmpLoadSourceNatural.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['PreBmpLoadSourceNatural'])

        # Data from excel sheets are saved to class attributes.
        self.PreBmpLoadSourceNatural = self.data['PreBmpLoadSourceNatural']
