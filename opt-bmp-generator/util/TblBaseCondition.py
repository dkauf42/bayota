from util.ExcelDataTable import ExcelDataTable

reportsdir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/CAST_reports/'


class BaseCondition(ExcelDataTable):
    def __init__(self, filename='2016Progress_BaseConditions.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['Landuse Acres'])

        # Data from excel sheets are saved to class attributes.
        self.LSacres = self.data['Landuse Acres']
