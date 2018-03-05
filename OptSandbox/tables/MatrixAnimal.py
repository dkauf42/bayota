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
        print("\nMatrixAnimal:identifyhardupperbounds: ya'ad table...")
        print(self.yaad_table.head())
        old_keys = [x for x in self.yaad_table['AnimalName']]
        new_vals = [x for x in self.yaad_table['AnimalUnits']]
        replace_vals = dict(zip(old_keys, new_vals))

        indexindex = self.eligibleparametermatrix.index.names.index('AnimalName')
        for index, row in tqdm(self.eligibleparametermatrix.iterrows(), total=len(self.eligibleparametermatrix.index)):
            # iterate through the load sources
            animalname = row.name[indexindex]
            hub_value = replace_vals[animalname]
            print('row animal name is <%s>, so replacing ones with %f' % (animalname, hub_value))
            row[row == 1] = hub_value