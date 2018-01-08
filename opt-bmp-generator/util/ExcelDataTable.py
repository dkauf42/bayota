import pandas as pd


class ExcelDataTable:
    def __init__(self, filename='', dirpath='', sheet_names=None):

        self.filename = filename
        self.fullpath = dirpath + self.filename
        self.sheet_names = sheet_names

        self.data = None
        self.loadsheets()

    def __getitem__(self, item):
        return getattr(self, item)

    def loadsheets(self):
        self.data = pd.read_excel(self.fullpath, sheet_name=self.sheet_names)
