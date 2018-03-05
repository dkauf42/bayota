from tables.MatrixBase import MatrixBase


class MatrixSand(MatrixBase):
    def __init__(self, name='', geographies=None, agencies=None, queries=None):
        """Sub-class for Septic, Agriculture, Natural, and Developed (SAND) BMPs"""

        # "Ya'ad" (load sources, agencies, geo, units, amounts, etc.) table is generated.
        self.yaad_table = queries.loadsources.get_yaad_for_sand(geographies=geographies, agencies=agencies)

        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.tables.srcdata.allbmps_shortnames)

    def _identifyhardupperbounds(self):
        #self.eligibleparametermatrix.
        pass
