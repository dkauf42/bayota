from tables.ExcelDataTable import ExcelDataTable

srcdatadir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/source_and_base/2016progress/'


class SourceData(ExcelDataTable):
    def __init__(self, filename='SourceData.xlsx', dirpath=srcdatadir):

        sheet_names = ['Geographic References', 'BMP Definitions', 'Efficiency BMPs',
                       'Load Source Conversion BMPs', 'Load Reduction BMPs',
                       'Animal BMPs', 'BMP Load Source Groups', 'Load Source Group Components',
                       'Agencies', 'Load Source Definitions']

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath, sheet_names=sheet_names)

        # Data from excel sheets are saved to class attributes.
        self.georefs = self.data[sheet_names[0]]
        self.bmpDefinitions = self.data[sheet_names[1]]
        self.efficiencyBMPs = self.data[sheet_names[2]]
        self.sourceconversionBMPs = self.data[sheet_names[3]]
        self.loadreductionBMPs = self.data[sheet_names[4]]
        self.animalBMPs = self.data[sheet_names[5]]
        self.sourcegrps = self.data[sheet_names[6]]  # shows load source groups to which each bmp is applicable
        self.sourcegrpcomponents = self.data[sheet_names[7]]  # shows load sources represented by each LS group
        self.agencies = self.data[sheet_names[8]]  # Columns of interest: 'AgencyCode' and 'AgencyType'
        self.lsdefinitions = self.data[sheet_names[9]]

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

    def findbmptype(self, bmpshortname_orlist=''):
        if isinstance(bmpshortname_orlist, str):
            thesebmptypes = self.__singlebmptype(bmpshortname_orlist)
        elif isinstance(bmpshortname_orlist, list):
            if all(isinstance(item, str) for item in bmpshortname_orlist): # check iterable for stringness of all items.
                thesebmptypes = []
                for item in bmpshortname_orlist:
                    thesebmptypes.append(self.__singlebmptype(item))
            else:
                raise ValueError('unexpected type found in list')
        else:
            raise ValueError('unexpected type')
        return thesebmptypes

    def __singlebmptype(self, bmpshortname=''):
        bmptype = ''
        numtypes = 0
        if bmpshortname in self.efficiencyBMPs['BMPShortName'].values:
            bmptype = 'efficiency'
            numtypes += 1
        if bmpshortname in self.sourceconversionBMPs['BMPShortName'].values:
            bmptype = 'sourceconversion'
            numtypes += 1
        if bmpshortname in self.loadreductionBMPs['BMPShortName'].values:
            bmptype = 'loadreduction'
            numtypes += 1
        if bmpshortname in self.animalBMPs['BMPShortName'].values:
            bmptype = 'animal'
            numtypes += 1

        if numtypes == 0:
            if bmpshortname in self.bmpDefinitions['BMPShortName'].values:
                df = self.bmpDefinitions
                bmptype = df[df['BMPType'].notnull() & (df['BMPShortName'] == bmpshortname)]['BMPType'].iloc[0]
                numtypes += 1
            else:
                raise ValueError('No BMP type found for "%s"' % bmpshortname)
        elif numtypes > 1:
            raise ValueError('More than one BMP type found for "%s"' % bmpshortname)

        return bmptype

    def list_bmps_by_loadsource(self):
        pass
