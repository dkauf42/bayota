from scipy import sparse
import pandas as pd


class PossibilitiesMatrix:
    def __init__(self, sasobj=None, sourcedataobj=None):
        """Create a sparse matrix with rows=seg-agency-sources X columns=BMPs
        """
        self.data = None
        self.__create_matrix(sasobj, sourcedataobj.allbmps_shortnames)

        self.bmpdict = None
        self.__dict_of_bmps_by_loadsource(sourcedataobj, sasobj.all_sas.LoadSource.unique())

    def __create_matrix(self, sasobj, allbmps):
        df = pd.DataFrame(data=sasobj.sas_indices, columns=allbmps)

        df.sort_index(axis=0, inplace=True, sort_remaining=True)
        df.sort_index(axis=1, inplace=True, sort_remaining=True)

        self.data = df

    def __dict_of_bmps_by_loadsource(self, srcdataobj, load_sources):
        """ Generate a dictionary of BMPs that are eligible for every load source """
        ls_to_bmp_dict = {}
        for ls in load_sources:
            # Get the Load Source groups that this Load source is in.
            loadsourcegroups = srcdataobj.get(sheetabbrev='sourcegrpcomponents', getcolumn='LoadSourceGroup',
                                              by='LoadSource', equalto=ls)  # pandas.core.series.Series
            bmplist = []  # Create a list to store the data
            for x in loadsourcegroups:  # iterate through the load source groups
                # Get the BMPs that can be applied on this load source group
                thesebmps = srcdataobj.get(sheetabbrev='sourcegrps', getcolumn='BmpShortName',
                                           by='LoadSourceGroup', equalto=x).tolist()
                bmplist += thesebmps

            bmplist = self.removedups(bmplist)
            ls_to_bmp_dict[ls] = bmplist

        self.bmpdict = ls_to_bmp_dict

    def return_sparse(self):
        sparsedf = sparse.coo_matrix(self.data.fillna(0))
        print('Density of sparse matrix is %f' % (sparsedf.getnnz() / (sparsedf.shape[0] * sparsedf.shape[1])))
        return sparsedf

    @staticmethod
    def removedups(listwithduplicates):
        """ Code to remove duplicate elements"""
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list

