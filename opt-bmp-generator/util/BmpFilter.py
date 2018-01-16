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
        overallbmplist = []
        totalnumbmps = 0
        n = len(sasobj.all_sas.index)
        for index, row in tqdm(sasobj.all_sas.iterrows(), total=n):  # iterate through the load sources

            # Mark the eligible BMPs for each Load Source with a 999 instead of a NaN
            bmplist = possmatrix.bmpdict[row.LoadSource]
            possmatrix.data.loc[(index[0], index[1], row.LoadSource), bmplist] = 1

            bmplistoflists.append(bmplist)
            totalnumbmps += len(bmplist)
            overallbmplist += bmplist

        overallbmplist = possmatrix.removedups(overallbmplist)
        overallbmptypes = srcdataobj.findbmptype(overallbmplist)
        print('length of overall bmp list: %d' % len(overallbmplist))
        print(overallbmplist)

        diffbmps = set(possmatrix.data.columns.tolist()).symmetric_difference(set(overallbmplist))
        print('- There are %d differences between the possibilities matrix BMPs and OverallBMPlist:' % len(diffbmps))
        print(diffbmps)

        print('- Possibilities matrix dimensions are : %s' % (possmatrix.data.shape,))
        print('- Possibilities matrix is made up of %d nonzero and '
              '%d null elements, out of %d total elements' % (possmatrix.data.sum().sum(),
                                                              possmatrix.data.isnull().sum().sum(),
                                                              possmatrix.data.shape[0] * possmatrix.data.shape[1]))

        self.geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
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

