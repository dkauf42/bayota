import csv
import time

writedir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC-ResearchScientist-Optimization/' \
              'Optimization_Tool/2-ExperimentFolder/data_tables/inputs_generated_by_cast_opt_tests/'


class InputsToCast:
    def __init__(self, possmatrixobj=None):
        self.template = None
        self.df = None
        self.possmatrixobj = possmatrixobj

        self.headers_land = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation',
                             'BmpShortname', 'GeographyName', 'LoadSourceGroup', 'Amount', 'Unit']
        self.headers_animal = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation',
                               'BmpShortname', 'GeographyName', 'AnimalGroup', 'LoadSourceGroup',
                               'Amount', 'Unit', 'NReductionFraction', 'PReductionFraction']
        self.headers_manure = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation',
                               'BmpShortname', 'GeographyName', 'AnimalGroup', 'LoadSourceGroup',
                               'Amount', 'Unit', 'NReductionFraction', 'PReductionFraction']

    def matrix_to_table(self):

        stacked_ndas = self.possmatrixobj.ndas.stack()
        stacked_anim = self.possmatrixobj.anim.stack()
        stacked_manu = self.possmatrixobj.manu.stack()
        print(stacked_ndas.head())
        stacked_ndas.to_csv('testwrite_stacked_ndas_matrix.csv')
        stacked_anim.to_csv('testwrite_stacked_anim_matrix.csv')
        stacked_manu.to_csv('testwrite_stacked_manu_matrix.csv')

    def create_landbmp_file(self, datatowrite):
        self.writecsv(filename=writedir + 'landbmp_test' + time.strftime("%Y%m%d%H%M%S") + '.csv',
                      headers=self.headers_land,
                      datatowrite=datatowrite)

    def create_animalbmp_file(self, datatowrite):
        self.writecsv(filename=writedir + 'animalbmp_test' + time.strftime("%Y%m%d%H%M%S") + '.csv',
                      headers=self.headers_animal,
                      datatowrite=datatowrite)

    def create_manurebmp_file(self, datatowrite):
        self.writecsv(filename=writedir + 'landbmp_test' + time.strftime("%Y%m%d%H%M%S") + '.csv',
                      headers=self.headers_manure,
                      datatowrite=datatowrite)

    @staticmethod
    def writecsv(filename, headers, datatowrite):
        with open(filename, 'wb') as f:
            w = csv.writer(f)
            w.writerow(headers)
            for data in datatowrite:
                w.writerow(data)
