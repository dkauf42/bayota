import scipy
import numpy as np
import pandas as pd


class PossibilitiesMatrix:
    def __init__(self, sasobj=None, allbmps=None):
        """Create a sparse matrix with rows=seg-agency-sources X columns=BMPs
        """
        self.data = None
        self._create_matrix(sasobj, allbmps)

    def _create_matrix(self, sasobj, allbmps):
        df = pd.DataFrame(data=sasobj.sas_indices, columns=allbmps)

        df.sort_index(axis=0, inplace=True, sort_remaining=True)
        df.sort_index(axis=1, inplace=True, sort_remaining=True)

        self.data = df

