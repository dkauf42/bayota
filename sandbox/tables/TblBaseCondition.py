from sandbox.tables.ExcelDataTable import ExcelDataTable
from sandbox.__init__ import get_datadir

reportsdir = get_datadir()


class BaseCondition(ExcelDataTable):
    def __init__(self, filename='baseconditions2016progressV9.xlsx', dirpath=reportsdir):

        sheet_names = ['Animal Counts', 'Landuse Acres', 'Septic Systems']

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath, sheet_names=sheet_names)

        # Data from excel sheets are saved to class attributes.
        self.animalcounts = self.data[sheet_names[0]]
        self.LSacres = self.data[sheet_names[1]]
        self.septicsystems = self.data[sheet_names[2]]
