import csv
import time
import pandas as pd
from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


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
        self.tables = optinstance.queries.tables

        self.headers_land = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                             'GeographyName', 'LoadSourceGroup', 'Amount', 'Unit']
        self.headers_animal = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                               'GeographyName', 'AnimalGroup', 'LoadSourceGroup',
                               'Amount', 'Unit', 'NReductionFraction', 'PReductionFraction']
        self.headers_manure = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                               'FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup',
                               'Amount', 'Unit']

    def matrix_to_table(self):
        """Convert an M x N parametermatrix to a stacked (MxN) x 1 Series, and then to a DataFrame"""

        # **** LAND ****
        df_l = self.possmatrixobj['ndas'].scenariomatrix.stack()
        #print(df_l.index.names)  # 'LandRiverSegment', 'Agency', 'LoadSource', 'BmpShortname'
        newindexnames = ['GeographyName', 'AgencyCode', 'LoadSourceGroup', 'BmpShortname']
        df_l.index.rename(newindexnames, inplace=True)
        df_l.name = 'Amount'
        df_l = pd.DataFrame(df_l)
        # Make a new column with the State Abbreviation associated with that row's LRSeg ID
        df_l.reset_index(inplace=True)  # convert multiindexes into regular columns
        geodf = self.tables.srcdata.georefs.loc[:, ['StateAbbreviation', 'LandRiverSegment']]
        df_l = pd.merge(left=df_l, right=geodf, left_on='GeographyName', right_on='LandRiverSegment')
        # Add additional necessary columns
        df_l['Unit'] = ['Acres'] * len(df_l['Amount'])
        df_l['StateUniqueIdentifier'] = ['beebop'] * len(df_l['Amount'])
        df_l.reset_index(inplace=True)
        df_l = df_l[self.headers_land]
        df_l['AgencyCode'] = self.tables.agencytranslate_fromnames(df_l['AgencyCode'])

        # **** ANIMAL ****
        df_a = self.possmatrixobj['animal'].scenariomatrix.stack()
        #print(df_a.index.names)  # 'FIPS', 'AnimalName', 'LoadSource', 'BmpShortname'
        newindexnames = ['GeographyName', 'AnimalGroup', 'LoadSourceGroup', 'BmpShortname']
        df_a.index.rename(newindexnames, inplace=True)
        df_a.name = 'Amount'
        df_a = pd.DataFrame(df_a)
        # Make a new column with the State Abbreviation associated with that row's LRSeg ID
        df_a.reset_index(inplace=True)  # convert multiindexes into regular columns
        geodf = self.tables.srcdata.georefs.loc[:, ['StateAbbreviation', 'FIPS']]
        df_a = pd.merge(left=df_a, right=geodf, left_on='GeographyName', right_on='FIPS')
        # Add additional necessary columns
        df_a['Unit'] = 'Animal Count'
        df_a['AgencyCode'] = ['NONFED'] * len(df_a['Amount'])
        df_a['StateUniqueIdentifier'] = ['beebop'] * len(df_a['Amount'])
        df_a['NReductionFraction'] = [''] * len(df_a['Amount'])
        df_a['PReductionFraction'] = [''] * len(df_a['Amount'])
        df_a.reset_index(inplace=True)
        df_a = df_a[self.headers_animal]
        #print(df_a.head())

        # **** MANURE ****
        df_m = self.possmatrixobj['manure'].scenariomatrix.stack()
        #print(df_m.index.names)  # 'FIPSFrom', 'FIPSTo', 'AnimalName', 'Loadsource', 'BmpShortname'
        newindexnames = ['FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup', 'BmpShortname']
        df_m.index.rename(newindexnames, inplace=True)
        df_m.name = 'Amount'
        df_m = pd.DataFrame(df_m)
        # Make a new column with the State Abbreviation associated with that row's LRSeg ID
        df_m.reset_index(inplace=True)  # convert multiindexes into regular columns
        geodf = self.tables.srcdata.georefs.loc[:, ['StateAbbreviation', 'FIPS']]
        df_m = pd.merge(left=df_m, right=geodf, left_on='FIPSFrom', right_on='FIPS')
        # Add additional necessary columns
        df_m['Unit'] = 'WET TONS'
        df_m['AgencyCode'] = ['NONFED'] * len(df_m['Amount'])
        df_m['StateUniqueIdentifier'] = ['beebop'] * len(df_m['Amount'])
        df_m.reset_index(inplace=True)
        df_m = df_m[self.headers_manure]

        df_l.to_csv(writedir + 'testwrite_InputsToCast_stacked_ndas_matrix.txt',
                            sep='\t', header=True, index=False, line_terminator='\r\n')
        df_a.to_csv(writedir + 'testwrite_InputsToCast_stacked_anim_matrix.txt',
                            sep='\t', header=True, index=False, line_terminator='\r\n')
        df_m.to_csv(writedir + 'testwrite_InputsToCast_stacked_manu_matrix.txt',
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

