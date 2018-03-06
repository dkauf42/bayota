from tables.MatrixBase import MatrixBase
from tqdm import tqdm  # Loop progress indicator module


class MatrixAnimal(MatrixBase):
    def __init__(self, name='', geographies=None, queries=None):
        """Sub-class for Animal BMPs"""

        # "Ya'ad" (load sources, agencies, geo, units, amounts, etc.) table is generated.
        self.yaad_table = queries.loadsources.get_yaad_for_animal(geographies=geographies)

        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.tables.srcdata.allbmps_shortnames)

    def identifyhardupperbounds(self):
        old_key_animal = [x for x in self.yaad_table['AnimalName']]
        old_key_fips = [x for x in self.yaad_table['FIPS']]
        new_vals = [x for x in self.yaad_table['AnimalUnits']]
        replace_vals = dict(zip(zip(old_key_animal, old_key_fips), new_vals))

        index_animal = self.eligibleparametermatrix.index.names.index('AnimalName')
        index_fips = self.eligibleparametermatrix.index.names.index('FIPS')
        for index, row in tqdm(self.eligibleparametermatrix.iterrows(), total=len(self.eligibleparametermatrix.index)):
            # iterate through the load sources
            animalname = row.name[index_animal]
            fipscode = row.name[index_fips]

            hub_value = replace_vals[(animalname, fipscode)]
            #print('row <animalname: %s> \n'
            #      '    <fips:       %s>\n '
            #      '     so replacing ones with %f' % (animalname, fipscode, hub_value))
            row[row == 1] = hub_value