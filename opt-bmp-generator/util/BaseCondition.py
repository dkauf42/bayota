import pandas as pd

reportsdir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/CAST_reports/'


class BaseCondition:
    def __init__(self, filename='2016Progress_BaseConditions.xlsx'):

        self.filename = filename
        self.fullpath = reportsdir + self.filename

        self.LSacres = None

        self.load()

    def __getitem__(self, item):
        return getattr(self, item)

    def load(self):
        data = pd.read_excel(self.fullpath, sheet_name=['Landuse Acres'])
        self.LSacres = data['Landuse Acres']

    def get(self, sheetabbrev='LSacres', getcolumn='PreBMPAcres', by='LoadSource', equalto='Ag Open Space'):
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