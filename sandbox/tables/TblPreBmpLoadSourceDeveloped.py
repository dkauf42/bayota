from sandbox.tables.ExcelDataTable import ExcelDataTable
from sandbox.__init__ import get_datadir

reportsdir = get_datadir()


class TblPreBmpLoadSourceDeveloped(ExcelDataTable):
    def __init__(self, filename='2016 Progress V8 - COPY_PreBmpLoadSourceDeveloped.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['PreBmpLoadSourceDeveloped'])

        # Data from excel sheets are saved to class attributes.
        self.PreBmpLoadSourceDeveloped = self.data['PreBmpLoadSourceDeveloped']
