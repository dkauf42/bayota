import pandas as pd


class ExcelDataTable:
    def __init__(self, filename='', dirpath='', sheet_names=None):
        """A parent class for various data tables that are excel formatted"""

        self.filename = filename
        self.fullpath = dirpath + self.filename
        self.sheet_names = sheet_names

        self.data = None
        self._loadsheets()

    def __getitem__(self, item):
        return getattr(self, item)

    def _loadsheets(self):
        self.data = pd.read_excel(self.fullpath, sheet_name=self.sheet_names)

    def get(self, sheetabbrev='georefs', getcolumn='LandRiverSegment', by='CountyName', equalto='Anne Arundel'):
        """Get the values from rows that match criteria in another data column

        Parameters:
            sheetabbrev (str): Excel Sheet Abbreviation; For example: georefs, efficiencyBMPs, deliveryfactors, etc.
            getcolumn (str): For example: LandRiverSegment, LoadSource, etc.
            by (str): For example: CountyName, LandRiverSegment, etc.
            equalto (str): For example: Anne Arundel, MD, N24003WL0_4390_0000, etc.

        Returns:
            (pandas dataframe): a subset of the original table

        Example:
            | sheetabbrev='georefs', getcolumn='LandRiverSegment', by='CountyName', equalto='Anne Arundel'
            | sheetabbrev='LSacres', getcolumn='PreBMPAcres', by='LoadSource', equalto='Ag Open Space'

        """
        df = self[sheetabbrev]

        # Select all cases where the values are not missing and the by column is equal to equalto
        retval = df[df[getcolumn].notnull() & (df[by] == equalto)][getcolumn]

        return retval
