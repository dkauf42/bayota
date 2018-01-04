from util.geoobj import GeoObj


class StateObj(GeoObj):
    def __init__(self, *args, **kwargs):
        GeoObj.__init__(self, geotype='state', *args, **kwargs)  # Use the __init__ of the superclass

    def __str__(self):
        """
        Example Print statement:

        State Object named <MD>
        with 521 LRSs

        """
        name_str = 'State Object named <' + self.geoname + '>'
        lrs_str = '\n with %d LRSs' % self.land_river_segments.count()
        ls_str = '\n with %d total nonzero Load Sources in all LRSs' % self.num_load_sources
        return name_str + lrs_str + ls_str
