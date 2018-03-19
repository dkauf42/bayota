import numpy as np
import pandas as pd
from tables.MatrixBase import MatrixBase


class MatrixAnimal(MatrixBase):
    def __init__(self, name='', geographies=None, queries=None):
        """Sub-class for Animal BMPs"""

        # "Ya'ad" (load sources, agencies, geo, units, amounts, etc.) table is generated.
        self.yaad_table = queries.loadsources.get_yaad_for_animal(geographies=geographies)

        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.tables.srcdata.allbmps_shortnames)

    def identifyhardupperbounds(self):
        # use numpy representation of eligibleparametermatrix
        hub_table = self.eligibleparametermatrix.values *\
                    self.yaad_table['AnimalUnits'].values[:, np.newaxis]
        self.hardupperboundmatrix = pd.DataFrame(hub_table, index=self.eligibleparametermatrix.index,
                                                            columns=self.eligibleparametermatrix.columns)
        #self.hardupperboundmatrix.to_csv('./output/testcompare_animal_hubtable_fromnumpy.csv')

    def identifyhardlowerbounds(self):
        hlb_table = self.eligibleparametermatrix.values * 0
        self.hardlowerboundmatrix = pd.DataFrame(hlb_table, index=self.eligibleparametermatrix.index,
                                                            columns=self.eligibleparametermatrix.columns)

        # old_key_animal = [x for x in self.yaad_table.index.get_level_values('AnimalName')]
        # old_key_fips = [x for x in self.yaad_table.index.get_level_values('FIPS')]
        # new_vals = [x for x in self.yaad_table['AnimalUnits']]
        # replace_vals = dict(zip(zip(old_key_animal, old_key_fips), new_vals))
        #
        # index_animal = self.eligibleparametermatrix.index.names.index('AnimalName')
        # index_fips = self.eligibleparametermatrix.index.names.index('FIPS')
        #
        # self.yaad_table.to_csv('./output/testcompare_animal_yaadtable.csv')
        # self.eligibleparametermatrix.to_csv('./output/testcompare_animal_eligibilitymatrix.csv')
        #
        # for index, row in tqdm(self.eligibleparametermatrix.iterrows(),
        #                        total=len(self.eligibleparametermatrix.index), file=sys.stdout):
        #     # iterate through the load sources
        #     animalname = row.name[index_animal]
        #     fipscode = row.name[index_fips]
        #
        #     hub_value = replace_vals[(animalname, fipscode)]
        #     #print('row <animalname: %s> \n'
        #     #      '    <fips:       %s>\n '
        #     #      '     so replacing ones with %f' % (animalname, fipscode, hub_value))
        #     row[row == 1] = hub_value