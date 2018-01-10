from tables.ExcelDataTable import ExcelDataTable

srcdatadir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/source_and_base/2016progress/'


class SourceData(ExcelDataTable):
    def __init__(self, filename='SourceData.xlsx', dirpath=srcdatadir):

        sheet_names = ['Geographic References', 'Efficiency BMPs',
                       'Load Source Conversion BMPs', 'Load Reduction BMPs',
                       'BMP Load Source Groups', 'Load Source Group Components',
                       'Agencies', 'Load Source Definitions']

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath, sheet_names=sheet_names)

        # Data from excel sheets are saved to class attributes.
        self.georefs = self.data[sheet_names[0]]
        self.efficiencyBMPs = self.data[sheet_names[1]]
        self.sourceconversionBMPs = self.data[sheet_names[2]]
        self.loadreductionBMPs = self.data[sheet_names[3]]
        self.loadsourcegroups = self.data[sheet_names[4]]  # shows load source groups to which each bmp is applicable
        self.loadsourcegroupcomponents = self.data[sheet_names[5]]  # shows load sources represented by each LS group
        self.agencies = self.data[sheet_names[6]]  # Columns of interest: 'AgencyCode' and 'AgencyType'
        self.lsdefinitions = self.data[sheet_names[7]]

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
