from util.geoobj import GeoObj


class CountyObj(GeoObj):
    def __init__(self, *args, **kwargs):
        GeoObj.__init__(self, geotype='county', *args, **kwargs)  # Use the __init__ of the superclass

    def __str__(self):
        """
        Example Print statement:

        County Object named <Anne Arundel>
        with 31 LRSs

        """
        name_str = 'County Object named <' + self.geoname + '>'
        lrs_str = '\n with %d LRSs' % self.land_river_segments.count()
        ls_str = '\n with %d total nonzero Load Sources in all LRSs' % self.num_load_sources
        return name_str + lrs_str + ls_str
