from tables.ExcelDataTable import ExcelDataTable

reportsdir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/source_and_base/2016progress/'


class TblPreBmpLoadSourceDeveloped(ExcelDataTable):
    def __init__(self, filename='2016 Progress V8 - COPY_PreBmpLoadSourceDeveloped.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['PreBmpLoadSourceDeveloped'])

        # Data from excel sheets are saved to class attributes.
        self.PreBmpLoadSourceDeveloped = self.data['PreBmpLoadSourceDeveloped']
