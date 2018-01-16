from tqdm import tqdm  # Loop progress indicator module


class BmpFilter:
    def __init__(self, sasobj=None, sourcedataobj=None, possmatrix=None):
        """Find the segment - agency - source combinations available in the specified options.
        """
        self.geo_seg_source_bmps = None
        self.filter_from_sas(sasobj, sourcedataobj, possmatrix)

    def filter_from_sas(self, sasobj, srcdataobj, possmatrix):
        # Get all the BMPs that are possible on the set of Load sources
        self.geo_seg_source_bmps = sasobj.all_sas.copy()
        bmplistoflists = []  # Create a list to store the data
        bmptypeslistoflists = []
        overallbmplist = []
        totalnumbmps = 0
        n = len(sasobj.all_sas.index)
        for index, row in tqdm(sasobj.all_sas.iterrows(), total=n):  # iterate through the load sources
            # Get the Load Source groups that this Load source is in.
            loadsourcegroups = srcdataobj.get(sheetabbrev='sourcegrpcomponents', getcolumn='LoadSourceGroup',
                                              by='LoadSource', equalto=row.LoadSource)  # pandas.core.series.Series

            bmplist = []  # Create a list to store the data
            for x in loadsourcegroups:  # iterate through the load source groups
                # Get the BMPs that can be applied on this load source group
                thesebmps = srcdataobj.get(sheetabbrev='sourcegrps', getcolumn='BmpShortName',
                                           by='LoadSourceGroup', equalto=x).tolist()
                bmplist += thesebmps
                for b in thesebmps:
                    # Put a 999 in the possmatrix at this (i) seg-agency-source and (j) bmp coordinate
                    possmatrix.data.loc[(index[0], index[1], row.LoadSource), b] = 999

            bmplist = self.removedups(bmplist)
            bmplistoflists.append(bmplist)
            totalnumbmps += len(bmplist)
            overallbmplist += bmplist

            # For each BMP, also figure out which type it is
            thesebmptypes = srcdataobj.findbmptype(bmplist)
            bmptypeslistoflists.append(thesebmptypes)
            # print('"bmplist" has %d BMPs for load source "%s"' % (len(bmplist), row.LoadSource))

        possmatrix.data.to_csv('testwrite_possmatrix.csv')
        overallbmplist = self.removedups(overallbmplist)
        overallbmptypes = srcdataobj.findbmptype(overallbmplist)
        print('length of overall bmp list: %d' % len(overallbmplist))
        print(overallbmplist)
        print(overallbmptypes)

        self.geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
        self.geo_seg_source_bmps['eligible_bmps_types'] = bmptypeslistoflists
        print('total no. of eligible BMPs: <%d>' % totalnumbmps)

        # Load Reduction BMPs
        # TODO: Get data from

        # Animal BMPs
        # TODO: Get data from BaseCondition 'Animal Counts' spreadsheet

        # Manure BMPs
        # TODO: Get data from ManureTonsProduced spreadsheet

        # Septic Systems
        # TODO: Get data from BaseCondition 'Septic Systems' spreadsheet

        #print(self.geo_seg_source_bmps.head())
        #print(bmplist[0])
        self.geo_seg_source_bmps.to_csv('testwrite_geo_seg_source_bmps.csv')

    @staticmethod
    def removedups(listwithduplicates):
        """ Python code to remove duplicate elements"""
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list
