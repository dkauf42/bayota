import numpy as np
import pandas as pd
from sandbox.matrices.MatrixBase import MatrixBase
from sandbox.tables.TblJeeves import TblJeeves


class MatrixSand(MatrixBase):
    def __init__(self, name='', geographies=None, agencies=None, sectors=None, queries=None):
        """Sub-class for Septic, Agriculture, Natural, and Developed (SAND) BMPs"""

        # "Ya'ad" (load sources, agencies, geo, units, amounts, etc.) table is generated.
        #self.yaad_table = queries.loadsources.get_yaad_for_sand(geographies=geographies, agencies=agencies)

        lrsegids = queries.lrsegids_from(lrsegnames=geographies)
        agencyids = queries.agencyids_from(agencycodes=agencies)
        lrsegids = queries.sectorids_from(sectornames=agencies)

        self.yaad_table = queries.loadsources_from_lrseg_agency_sector(lrsegs=geographies,
                                                                       agencies=agencies,
                                                                       sectors=sectors)

        # TODO: yaad_table needs have multi-index or multiple dimensions!
        print(self.yaad_table)
        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.all_bmpnames())

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
