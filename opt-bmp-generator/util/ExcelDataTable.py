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

    def get(self, sheetabbrev='georefs', getcolumn='LandRiverSegment', by='CountyName', equalto='Anne Arundel'):
        """
        Get the values from rows that match criteria in another data column
        :param sheetabbrev: Excel Sheet Abbreviation; For example: georefs, efficiencyBMPs, deliveryfactors, etc.
        :param getcolumn: For example: LandRiverSegment, LoadSource, etc.
        :param by: For example: CountyName, LandRiverSegment, etc.
        :param equalto: For example: Anne Arundel, MD, N24003WL0_4390_0000, etc.
        :return: subset dataframe

        For example:
        sheetabbrev='georefs', getcolumn='LandRiverSegment', by='CountyName', equalto='Anne Arundel'
        sheetabbrev='LSacres', getcolumn='PreBMPAcres', by='LoadSource', equalto='Ag Open Space'
        """
        df = self[sheetabbrev]

        # Select all cases where the values are not missing and the by column is equal to equalto
        retval = df[df[getcolumn].notnull() & (df[by] == equalto)][getcolumn]

        return retval
