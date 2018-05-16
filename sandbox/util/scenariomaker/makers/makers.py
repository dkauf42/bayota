import os
import random
import numpy as np
import pandas as pd
from itertools import product

import dask.dataframe as dd

from sandbox.__init__ import get_outputdir
from sandbox.__init__ import inaws, s3, _S3BUCKET

writedir = get_outputdir()


class Maker(object):
    def __init__(self, decisionspace=None):
        """ Base class for all scenario makers in the optimizer engine

        """
        self.animalnametable = decisionspace.animal.nametable.copy()
        self.landnametable = decisionspace.land.nametable.copy()
        self.manurenametable = decisionspace.manure.nametable.copy()

        # self.scenarios = []

        self.scenarios_animal = []
        self.scenarios_land = []
        self.scenarios_manure = []

        self.longdf_animal = None
        self.longdf_land = None
        self.longdf_manure = None

    def __iter__(self):
        """ Generator to return the scenario objects, e.g. in For loops """
        # self.scenarios = [self.scenarios_animal, self.scenarios_land, self.scenarios_manure]
        for x, y in zip(['animal', 'land', 'manure'],
                        [self.scenarios_animal, self.scenarios_land, self.scenarios_manure]):
            yield x, y

    def write_to_tab_delimited_txt_file(self):
        # columns that are ids are translated to names, and scenarios are written to file.
        # for type_name, scenarios in self:
        #     i = 0
        #     for df in scenarios:
        #         # df = self.reorder_headers(table=df, tablename=type_name)
        #         df.to_csv(os.path.join(writedir, 'testwrite_CASTscenario_%s_%d.txt' % (type_name, i)),
        #                   sep='\t', header=True, index=False, line_terminator='\r\n')
        #         i += 1

        # Write concatenated scenario files with unique ScenarioNames
        df_animal = self.reorder_headers_with_scenarioname(self.longdf_animal, tablename='animal')
        dd_animal = dd.from_pandas(df_animal, npartitions=3)
        df_land = self.reorder_headers_with_scenarioname(self.longdf_land, tablename='land')
        dd_land = dd.from_pandas(df_land, npartitions=3)
        df_manure = self.reorder_headers_with_scenarioname(self.longdf_manure, tablename='manure')
        dd_manure = dd.from_pandas(df_manure, npartitions=3)

        animal_path = os.path.join(writedir, 'testwrite_CASTscenario_LongDF_%s.txt' % 'animal')
        df_animal.to_csv(animal_path, sep='\t', header=True, index=False, line_terminator='\r\n')

        land_path = os.path.join(writedir, 'testwrite_CASTscenario_LongDF_%s.txt' % 'land')
        df_land.to_csv(land_path, sep='\t', header=True, index=False, line_terminator='\r\n')

        manure_path = os.path.join(writedir, 'testwrite_CASTscenario_LongDF_%s.txt' % 'manure')
        df_manure.to_csv(manure_path, sep='\t', header=True, index=False, line_terminator='\r\n')

        if inaws:
            import boto3
            s3_client = boto3.client('s3')

            # Upload the file to S3
            s3_client.upload_file(animal_path, _S3BUCKET, 'animal_remote.txt')

            # Download the file from S3
            s3_client.download_file(_S3BUCKET, 'animal_remote.txt', 'hello2.txt')
            print(open('hello2.txt').read())
            # # bytes_to_write = df_animal.to_csv(None, sep='\t', header=True, index=False, line_terminator='\r\n').encode()
            # # with s3.open(os.path.join(_S3BUCKET, 'my-file_animal.txt'), mode='w') as f:
            # #     df_animal.to_csv(f, sep='\t', header=True, index=False, line_terminator='\r\n')
            # #     # f.write(bytes_to_write)
            # dd_animal.to_csv(os.path.join(_S3BUCKET, 'my-file_animal.txt'),
            #                  sep='\t', header=True, index=False, line_terminator='\r\n')
            # # bytes_to_write = df_land.to_csv(None, sep='\t', header=True, index=False, line_terminator='\r\n').encode()
            # # with s3.open(os.path.join(_S3BUCKET, 'my-file_land.txt'), mode='w') as f:
            # #     df_land.to_csv(f, sep='\t', header=True, index=False, line_terminator='\r\n')
            #     # f.write(bytes_to_write)
            # dd_land.to_csv(os.path.join(_S3BUCKET, 'my-file_land.txt'),
            #                  sep='\t', header=True, index=False, line_terminator='\r\n')
            # # bytes_to_write = df_manure.to_csv(None, sep='\t', header=True, index=False, line_terminator='\r\n').encode()
            # # with s3.open(os.path.join(_S3BUCKET, 'my-file_manure.txt'), mode='w') as f:
            # #     df_manure.to_csv(f, sep='\t', header=True, index=False, line_terminator='\r\n')
            #     # f.write(bytes_to_write)
            # dd_manure.to_csv(os.path.join(_S3BUCKET, 'my-file_manure.txt'),
            #                  sep='\t', header=True, index=False, line_terminator='\r\n')

            # Try Reading
            print('makers.write_to_tab_delimited_txt_file():')
            df = dd.read_csv(os.path.join(_S3BUCKET, 'my-file_manure.txt'), sep='\t')
            # with s3.open(os.path.join(_S3BUCKET, 'my-file_animal.txt'), mode='r') as f:
            #     # df = pd.read_csv(f, encoding='utf8', sep='\t')
            #     df = pd.read_csv(f, sep='\t')
            print(df.head())

    def add_bmptype_column(self, jeeves):
        for i in range(len(self.scenarios_animal)):
            self.scenarios_animal[i] = jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(self.scenarios_animal[i])
        for i in range(len(self.scenarios_land)):
            self.scenarios_land[i] = jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(self.scenarios_land[i])
        for i in range(len(self.scenarios_manure)):
            self.scenarios_manure[i] = jeeves.bmp. \
                appendBmpType_to_table_with_bmpshortnames(self.scenarios_manure[i])

    @staticmethod
    def softmax(x):
        """Calculate the softmax of a list of numbers x.

            Parameters:
                x : list of numbers

            Return:
                a list of the same length as x of non-negative numbers

            Examples:
                softmax([0.1, 0.2])
                    array([ 0.47502081,  0.52497919])
                softmax([-0.1, 0.2])
                    array([ 0.42555748,  0.57444252])
                softmax([0.9, -10])
                    array([  9.99981542e-01,   1.84578933e-05])
                softmax([0, 10])
                    array([  4.53978687e-05,   9.99954602e-01])
            """
        e_x = np.exp(x - np.max(x))
        out = e_x / e_x.sum()
        return out

    @staticmethod
    def reorder_headers(table, tablename):
        # TODO: rewrite this to pull the header order from the SQL Server Source Data
        header_order = dict()
        # Animal
        header_order['animal'] = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                  'GeographyName', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit',
                                  'NReductionFraction', 'PReductionFraction']
        # Land
        header_order['land'] = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                'GeographyName', 'LoadSourceGroup', 'Amount', 'Unit']
        # Manure
        header_order['manure'] = ['StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                  'FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit']

        return table[header_order[tablename]]

    @staticmethod
    def reorder_headers_with_scenarioname(table, tablename):
        # TODO: rewrite this to pull the header order from the SQL Server Source Data
        header_order = dict()
        # Animal
        header_order['animal'] = ['ScenarioName',
                                  'StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                  'GeographyName', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit',
                                  'NReductionFraction', 'PReductionFraction']
        # Land
        header_order['land'] = ['ScenarioName',
                                'StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                'GeographyName', 'LoadSourceGroup', 'Amount', 'Unit']
        # Manure
        header_order['manure'] = ['ScenarioName',
                                  'StateUniqueIdentifier', 'AgencyCode', 'StateAbbreviation', 'BmpShortname',
                                  'FIPSFrom', 'FIPSTo', 'AnimalGroup', 'LoadSourceGroup', 'Amount', 'Unit']

        return table[header_order[tablename]]

    @staticmethod
    def expand_grid(data_dict):
        """ Short method for generating all the combinations of values from a dictionary input"""
        rows = product(*data_dict.values())
        return pd.DataFrame.from_records(rows, columns=data_dict.keys())

    @staticmethod
    def _rand_integers(dataframe):
        howmanytoreplace = (dataframe == 1).sum().sum()
        dataframe[dataframe == 1] = random.sample(range(1, howmanytoreplace+1), howmanytoreplace)

    @staticmethod
    def _rand_matrix(dataframe):
        np.random.random(dataframe.shape)

    @staticmethod
    def _randomvaluesbetween(lower, upper):
        if type(lower) != type(upper):
            raise TypeError('Lower and Upper bound objects must be of the same type')

        if isinstance(lower, np.ndarray):
            shapetuple = upper.shape
            return (upper - lower) * np.random.random(shapetuple) + lower
        else:
            raise TypeError('Unrecognized type, not coded for.')
