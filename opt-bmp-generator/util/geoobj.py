import pandas as pd


class GeoObj:
    """Represent the LRS-Agency-LS-BMP combinations available within a particular county or state

        Parameters
        ----------
        geotype : `str`
            Type of geographic region: 'state', 'county'.
        name : `str`
            Name of state, county, etc.: e.g. 'Anne Arundel', 'MD', etc.
        srcdata : 'object'
            Source Data contained in a srcdataobj object.
        baseconditiondata : 'object'
            Base Condition Data contained in a basecondobj object

        Raises
        ------
        ValueError
            Raised when name does not exist in the geographic references of Source Data

    """
    def __init__(self, geotype='', name='', srcdata=None, baseconditiondata=None):
        self.geotype = geotype
        self.geoname = name
        self.srcdata = srcdata
        self.basecondata = baseconditiondata

        # Sanity check
        self.checkgeonameexists(self.geoname)

        # Properties of this geographic region are generated.
        #: pandas.core.series.Series: Unique LRSs
        self.land_river_segments = self.load_land_river_segments()
        #: pandas.core.frame.DataFrame: Nonzero Load Sources
        self.load_sources, self.num_load_sources = self.load_nonzeroloadsources()
        self.possible_BMPs = None

    def checkgeonameexists(self, name):
        if ~self.srcdata.georefs['CountyName'].str.contains(name).any() &\
                ~self.srcdata.georefs['StateAbbreviation'].str.contains(name).any():
            raise ValueError('Geographic name <%s> does not exist in Geographic References data' % name)

    def load_land_river_segments(self):
        """
        :return:
            pandas.core.series.Series: unique land-river-segments present in this geographic region
        """
        if self.geotype == 'state':
            byname = 'StateAbbreviation'
        elif self.geotype == 'county':
            byname = 'CountyName'
        else:
            raise ValueError('geotype not recognized')
        return self.srcdata.get(sheetabbrev='georefs',
                                getcolumn='LandRiverSegment',
                                by=byname,
                                equalto=self.geoname)

    def load_nonzeroloadsources(self):
        """
        :return:
            pandas.core.frame.DataFrame: two-column table of load sources for ALL land-river-segments.
            int: total number of nonzero load sources in ALL land-river-segments
        """
        x = 0
        lsdf = pd.DataFrame(columns=['lrs', 'lss'])
        for lrs in self.land_river_segments:
            lss = self.loadsources_by_lrs(lrs)
            x += lss.size

            thisdf = pd.DataFrame({'lrs': ''.join(lrs), 'lss': lss})
            lsdf = pd.concat((lsdf, thisdf))
        return lsdf, x

    def loadsources_by_lrs(self, lrs):
        """
        :param:
            string: land river segment
        :return:
            pandas.core.series.Series: preBMP load source acreage (if nonzero) for the specified land-river-segment
        """
        return self.basecondata.getnonzero(sheetabbrev='LSacres',
                                           getcolumn='LoadSource',
                                           by='LandRiverSegment',
                                           equalto=lrs,
                                           zerocheck='PreBMPAcres')
