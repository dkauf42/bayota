import pandas as pd
from itertools import product


class MatrixBase:
    def __init__(self, name='', row_indices=None, column_names=None):
        """A wrapper class for a possibility matrix needed for an optinstance"""
        self.name = name

        if (row_indices is None) | (column_names is None):
            self.matrix = pd.DataFrame()
        else:
            self.matrix = self.create_emptydf(row_indices=row_indices, column_names=column_names)

    def __getitem__(self, item):
        return getattr(self, item)

    def get_rows(self):
        pass

    def get_cols(self):
        pass

    @staticmethod
    def create_emptydf(row_indices, column_names):
        """ Short module-level function for generating the skeleton of a possibility-matrix"""
        df = pd.DataFrame(index=row_indices, columns=column_names)

        df.sort_index(axis=0, inplace=True, sort_remaining=True)
        df.sort_index(axis=1, inplace=True, sort_remaining=True)

        return df

    @staticmethod
    def expand_grid(data_dict):
        """ Short method for generating all the combinations of values from a dictionary input"""
        rows = product(*data_dict.values())
        return pd.DataFrame.from_records(rows, columns=data_dict.keys())
