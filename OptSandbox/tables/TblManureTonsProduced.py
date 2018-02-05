from tables.ExcelDataTable import ExcelDataTable

reportsdir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/' \
              'Optimization_Tool/2_ExperimentFolder/data_tables/source_and_base/2016progress/'


class ManureTonsProduced(ExcelDataTable):
    def __init__(self, filename='2016 Progress V8 - COPY_ManureTonsProduced.xlsx', dirpath=reportsdir):

        ExcelDataTable.__init__(self, filename=filename, dirpath=dirpath,
                                sheet_names=['ManureTonsProduced'])

        # Data from excel sheets are saved to class attributes.
        self.ManureTonsProduced = self.data['ManureTonsProduced']
