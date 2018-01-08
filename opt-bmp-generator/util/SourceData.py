from util.ExcelDataTable import ExcelDataTable

srcdatadir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/possibilities_calculation/'


class SourceData(ExcelDataTable):
    def __init__(self, filename='SourceData_wPossibilities.xlsx', dirpath=srcdatadir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['Geographic References', 'Efficiency BMPs',
                                             'Agencies', 'Load Source Definitions'])

        # Data from excel sheets are saved to class attributes.
        self.georefs = self.data['Geographic References']
        self.efficiencyBMPs = self.data['Efficiency BMPs']
        self.agencies = self.data['Agencies']  # Columns of interest: 'AgencyCode' and 'AgencyType'
        self.lsdefinitions = self.data['Load Source Definitions']

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
