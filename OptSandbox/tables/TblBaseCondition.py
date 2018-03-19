from tables.ExcelDataTable import ExcelDataTable
from OptSandbox.__init__ import get_data

reportsdir = get_data()


class BaseCondition(ExcelDataTable):
    def __init__(self, filename='baseconditions2017progressV4.xlsx', dirpath=reportsdir):

        sheet_names = ['Animal Counts', 'Landuse Acres', 'Septic Systems']

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath, sheet_names=sheet_names)

        # Data from excel sheets are saved to class attributes.
        self.animalcounts = self.data[sheet_names[0]]
        self.LSacres = self.data[sheet_names[1]]
        self.septicsystems = self.data[sheet_names[2]]
