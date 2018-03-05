from tables.MatrixBase import MatrixBase


class MatrixAnimal(MatrixBase):
    def __init__(self, name='', geographies=None, queries=None):
        """Sub-class for Animal BMPs"""

        # Load source with agencies, geo, etc. ("Ya'ad") table is generated.
        self.yaad_table = queries.loadsources.get_yaad_for_animal(geographies=geographies)

        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.tables.srcdata.allbmps_shortnames)

    def _identifyhardupperbounds(self):
        pass

