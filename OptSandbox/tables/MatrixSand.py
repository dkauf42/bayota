from tables.MatrixBase import MatrixBase


class MatrixSand(MatrixBase):
    def __init__(self, name='', row_indices=None, column_names=None):
        """Sub-class for Septic, Agriculture, Natural, and Developed (SAND) BMPs"""

        MatrixBase.__init__(self, name=name, row_indices=row_indices, column_names=column_names)
