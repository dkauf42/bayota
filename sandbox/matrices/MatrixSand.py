import numpy as np
import pandas as pd
from sandbox.matrices.MatrixBase import MatrixBase


class MatrixSand(MatrixBase):
    def __init__(self, name='', geographies=None, agencies=None, queries=None):
        """Sub-class for Septic, Agriculture, Natural, and Developed (SAND) BMPs"""

        # "Ya'ad" (load sources, agencies, geo, units, amounts, etc.) table is generated.
        self.yaad_table = queries.loadsources.get_yaad_for_sand(geographies=geographies, agencies=agencies)

        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.tables.srcdata.allbmps_shortnames)

    def identifyhardupperbounds(self):
        #numpy_start_time = timeit.default_timer()
        # use numpy representation of eligibleparametermatrix
        hub_table = self.eligibleparametermatrix.values * self.yaad_table['Amount'].values[:, np.newaxis]
        self.hardupperboundmatrix = pd.DataFrame(hub_table, index=self.eligibleparametermatrix.index,
                                                            columns=self.eligibleparametermatrix.columns)
        #self.hardupperboundmatrix.to_csv('./output/testcompare_sand_hubtable_fromnumpy.csv')
        #print("MatrixSand:identifyhardupperbounds: Numpy calc time", timeit.default_timer() - numpy_start_time)

    def identifyhardlowerbounds(self):
        hlb_table = self.eligibleparametermatrix.values * 0
        self.hardlowerboundmatrix = pd.DataFrame(hlb_table, index=self.eligibleparametermatrix.index,
                                                            columns=self.eligibleparametermatrix.columns)
