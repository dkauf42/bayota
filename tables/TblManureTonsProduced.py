from tables.ExcelDataTable import ExcelDataTable
from __init__ import get_data

reportsdir = get_data()


class ManureTonsProduced(ExcelDataTable):
    def __init__(self, filename='2016 Progress V8 - COPY_ManureTonsProduced.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['ManureTonsProduced'])

        # Data from excel sheets are saved to class attributes.
        self.ManureTonsProduced = self.data['ManureTonsProduced']
