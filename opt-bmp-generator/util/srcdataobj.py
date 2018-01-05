import pandas as pd

srcdatadir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/possibilities_calculation/'


class SrcDataObj:
    def __init__(self, filename='SourceData_wPossibilities.xlsx'):

        self.filename = filename
        self.fullpath = srcdatadir + self.filename

        # Data from Excel Sheets
        self.georefs = None
        self.efficiencyBMPs = None
        self.agencies = None  # Columns of interest: 'AgencyCode' and 'AgencyType'

        self.loadsrc()

    def __getitem__(self, item):
        return getattr(self, item)

    def loadsrc(self):
        data = pd.read_excel(self.fullpath, sheet_name=['Geographic References', 'Efficiency BMPs', 'Agencies'])

        # Data from Excel Sheets
        self.georefs = data['Geographic References']
        self.efficiencyBMPs = data['Efficiency BMPs']
        self.agencies = data['Agencies']

    def get(self, sheetabbrev='georefs', getcolumn='LandRiverSegment', by='CountyName', equalto='Anne Arundel'):
        """
        Get the values from rows that match criteria in another data column
        :param sheetabbrev: Excel Sheet Abbreviation; For example: georefs, efficiencyBMPs, deliveryfactors, etc.
        :param getcolumn: For example: LandRiverSegment, LoadSource, etc.
        :param by: For example: CountyName, LandRiverSegment, etc.
        :param equalto: For example: Anne Arundel, MD, N24003WL0_4390_0000, etc.
        :return: subset dataframe
        """
        df = self[sheetabbrev]

        # Select all cases where the values are not missing and the by column is equal to equalto
        retval = df[df[getcolumn].notnull() & (df[by] == equalto)][getcolumn]

        return retval
