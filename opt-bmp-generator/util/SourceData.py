from util.ExcelDataTable import ExcelDataTable

srcdatadir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/'


class SourceData(ExcelDataTable):
    def __init__(self, filename='SourceData_wPossibilities.xlsx', dirpath=srcdatadir):

        sheet_names = ['Geographic References', 'Efficiency BMPs',
                       'Load Source Conversion BMPs', 'Agencies',
                       'Load Source Definitions']

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath, sheet_names=sheet_names)

        # Data from excel sheets are saved to class attributes.
        self.georefs = self.data[sheet_names[0]]
        self.efficiencyBMPs = self.data[sheet_names[1]]
        self.sourceconversionBMPs = self.data[sheet_names[2]]
        self.agencies = self.data[sheet_names[3]]  # Columns of interest: 'AgencyCode' and 'AgencyType'
        self.lsdefinitions = self.data[sheet_names[4]]

    def getallnames(self, nametype):
        if nametype == 'LandRiverSegment':
            listofall = self.georefs[nametype].unique()
        elif nametype == 'CountyName':
            listofall = self.georefs[nametype].unique()
        elif nametype == 'StateAbbreviation':
            listofall = self.georefs[nametype].unique()
        elif (nametype == 'StateBasin') | (nametype == 'MajorBasin'):
            listofall = self.georefs['MajorBasin'].unique()
        elif nametype == 'AgencyCode':
            listofall = self.agencies[nametype].unique()
        elif nametype == 'Sector':
            listofall = self.lsdefinitions[nametype].unique()
        else:
            raise ValueError('Unrecognized nametype: "%s"' % nametype)
        return listofall

    def list_bmps_by_loadsource(self):
        pass
