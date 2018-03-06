import sys
from tables.MatrixBase import MatrixBase
from tqdm import tqdm  # Loop progress indicator module


class MatrixSand(MatrixBase):
    def __init__(self, name='', geographies=None, agencies=None, queries=None):
        """Sub-class for Septic, Agriculture, Natural, and Developed (SAND) BMPs"""

        # "Ya'ad" (load sources, agencies, geo, units, amounts, etc.) table is generated.
        self.yaad_table = queries.loadsources.get_yaad_for_sand(geographies=geographies, agencies=agencies)

        MatrixBase.__init__(self, name=name, row_indices=self.yaad_table.index,
                            column_names=queries.tables.srcdata.allbmps_shortnames)

    def identifyhardupperbounds(self):
        old_key_lrseg = [x for x in self.yaad_table['LandRiverSegment']]
        old_key_agency = [x for x in self.yaad_table['Agency']]
        old_key_loadsrc = [x for x in self.yaad_table['LoadSource']]
        new_vals = [x for x in self.yaad_table['Amount']]
        replace_vals = dict(zip(zip(old_key_lrseg, old_key_agency, old_key_loadsrc), new_vals))

        index_lrseg = self.eligibleparametermatrix.index.names.index('LandRiverSegment')
        index_agency = self.eligibleparametermatrix.index.names.index('Agency')
        index_loadsrc = self.eligibleparametermatrix.index.names.index('LoadSource')
        for index, row in tqdm(self.eligibleparametermatrix.iterrows(),
                               total=len(self.eligibleparametermatrix.index), file=sys.stdout):
            # iterate through the load sources
            lrseg = row.name[index_lrseg]
            agency = row.name[index_agency]
            loadsrc = row.name[index_loadsrc]

            hub_value = replace_vals[(lrseg, agency, loadsrc)]
            #print('row <lrseg:   %s>\n'
            #      '    <agency:  %s>\n '
            #      '    <loadsrc: %s>\n '
            #      '     so replacing ones with %f' % (lrseg, agency, loadsrc, hub_value))
            row[row == 1] = hub_value
        pass
