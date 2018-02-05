from tables.ExcelDataTable import ExcelDataTable

reportsdir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/' \
              'Optimization_Tool/2_ExperimentFolder/data_tables/source_and_base/2016progress/'


class BaseCondition(ExcelDataTable):
    def __init__(self, filename='2016ProgressV8-BaseConditions.xlsx', dirpath=reportsdir):

        sheet_names = ['Animal Counts', 'Landuse Acres', 'Septic Systems']

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath, sheet_names=sheet_names)

        # Data from excel sheets are saved to class attributes.
        self.animalcounts = self.data[sheet_names[0]]
        self.LSacres = self.data[sheet_names[1]]
        self.septicsystems = self.data[sheet_names[2]]
