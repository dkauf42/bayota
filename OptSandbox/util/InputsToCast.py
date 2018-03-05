import csv
import time
import pandas as pd

writedir = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/' \
              'Optimization_Tool/2_ExperimentFolder/data_tables/inputs_generated_by_cast_opt_tests/'


def writecsv(filename, headers, datatowrite):
    with open(filename, 'wb') as f:
        w = csv.writer(f)
        w.writerow(headers)
        for data in datatowrite:
            w.writerow(data)


class InputsToCast:
    def __init__(self, possmatrixobj=None, optinstance=None):
        """Write data matrices to tab-delimited (.txt) tables readable by CAST"""
        self.template = None
        self.df = None
        self.possmatrixobj = possmatrixobj
        self.tables = optinstance.tables

        self.headers_land = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                             'GeographyName', 'LoadSourceGroup', 'Amount', 'Unit']
        self.headers_animal = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                               'GeographyName', 'AnimalGroup', 'LoadSourceGroup',
                               'Amount', 'Unit', 'NReductionFraction', 'PReductionFraction']
        self.headers_manure = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                               'FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup',
                               'Amount', 'Unit']

    def matrix_to_table(self):
        """Convert an M x N matrix to a stacked (MxN) x 1 Series, and then to a DataFrame"""

        stacked_ndas = self.possmatrixobj['ndas'].matrix.stack()
        print(stacked_ndas.index.names)  # 'LandRiverSegment', 'Agency', 'LoadSource', 'BmpShortname'
        newindexnames = ['GeographyName', 'AgencyCode', 'LoadSourceGroup', 'BmpShortname']
        print(newindexnames)
        stacked_ndas.index.rename(newindexnames, inplace=True)
        stacked_ndas.name = 'Amount'
        stacked_ndas = pd.DataFrame(stacked_ndas)
        stacked_ndas['Unit'] = ['Acres'] * len(stacked_ndas['Amount'])
        stacked_ndas['StateAbbreviation'] = ['MD'] * len(stacked_ndas['Amount'])
        stacked_ndas['StateUniqueIdentifier'] = ['beebop'] * len(stacked_ndas['Amount'])
        stacked_ndas.reset_index(inplace=True)
        stacked_ndas = stacked_ndas[self.headers_land]
        stacked_ndas['AgencyCode'] = self.tables.agencytranslate_fromnames(stacked_ndas['AgencyCode'])
        print(stacked_ndas.head())

        stacked_anim = self.possmatrixobj['animal'].matrix.stack()
        print(stacked_anim.index.names)  # 'FIPS', 'AnimalName', 'LoadSource', 'BmpShortname'
        newindexnames = ['GeographyName', 'AnimalGroup', 'LoadSourceGroup', 'BmpShortname']
        print(newindexnames)
        stacked_anim.index.rename(newindexnames, inplace=True)
        stacked_anim.name = 'Amount'
        stacked_anim = pd.DataFrame(stacked_anim)
        stacked_anim['Unit'] = 'Animal Count'
        stacked_anim['AgencyCode'] = ['NONFED'] * len(stacked_anim['Amount'])
        stacked_anim['StateAbbreviation'] = ['MD'] * len(stacked_anim['Amount'])
        stacked_anim['StateUniqueIdentifier'] = ['beebop'] * len(stacked_anim['Amount'])
        stacked_anim['NReductionFraction'] = [''] * len(stacked_anim['Amount'])
        stacked_anim['PReductionFraction'] = [''] * len(stacked_anim['Amount'])
        stacked_anim.reset_index(inplace=True)
        stacked_anim = stacked_anim[self.headers_animal]
        print(stacked_anim.head())

        stacked_manu = self.possmatrixobj['manure'].matrix.stack()
        print(stacked_manu.index.names)  # 'FIPSFrom', 'FIPSTo', 'AnimalName', 'Loadsource', 'BmpShortname'
        newindexnames = ['FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup', 'BmpShortname']
        print(newindexnames)
        stacked_manu.index.rename(newindexnames, inplace=True)
        stacked_manu.name = 'Amount'
        stacked_manu = pd.DataFrame(stacked_manu)
        stacked_manu['Unit'] = 'WET TONS'
        stacked_manu['AgencyCode'] = ['NONFED'] * len(stacked_manu['Amount'])
        stacked_manu['StateAbbreviation'] = ['MD'] * len(stacked_manu['Amount'])
        stacked_manu['StateUniqueIdentifier'] = ['beebop'] * len(stacked_manu['Amount'])
        stacked_manu.reset_index(inplace=True)
        stacked_manu = stacked_manu[self.headers_manure]
        print(stacked_manu.head())

        #print(stacked_ndas.head())

        stacked_ndas.to_csv('./output/testwrite_InputsToCast_stacked_ndas_matrix.txt',
                            sep='\t', header=True, index=False, line_terminator='\r\n')
        stacked_anim.to_csv('./output/testwrite_InputsToCast_stacked_anim_matrix.txt',
                            sep='\t', header=True, index=False, line_terminator='\r\n')
        stacked_manu.to_csv('./output/testwrite_InputsToCast_stacked_manu_matrix.txt',
                            sep='\t', header=True, index=False, line_terminator='\r\n')

    def create_landbmp_file(self, datatowrite):
        writecsv(filename=writedir + 'landbmp_test' + time.strftime("%Y%m%d%H%M%S") + '.csv',
                 headers=self.headers_land,
                 datatowrite=datatowrite)

    def create_animalbmp_file(self, datatowrite):
        writecsv(filename=writedir + 'animalbmp_test' + time.strftime("%Y%m%d%H%M%S") + '.csv',
                 headers=self.headers_animal,
                 datatowrite=datatowrite)

    def create_manurebmp_file(self, datatowrite):
        writecsv(filename=writedir + 'landbmp_test' + time.strftime("%Y%m%d%H%M%S") + '.csv',
                 headers=self.headers_manure,
                 datatowrite=datatowrite)

