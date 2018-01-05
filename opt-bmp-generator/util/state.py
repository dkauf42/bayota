from util.geo import Geo


class State(Geo):
    def __init__(self, *args, **kwargs):
        Geo.__init__(self, geotype='state', *args, **kwargs)  # Use the __init__ of the superclass

    def __str__(self):
        """

        Example
        ------
        # Create a State Object representing Maryland
        MDState = State(name='MD', srcdataobj=srcdataobj, baseconditiondata=baseconditionobj)

        # Using a State's print statement:
        print(MDState)

        >> State Object named <MD>
        >>  with 521 LRSs

        """
        name_str = 'State Object named <' + self.geoname + '>'
        lrs_str = '\n with %d LRSs' % self.land_river_segments.count()
        ls_str = '\n with %d total nonzero Load Sources in all LRSs' % self.num_load_sources
        return name_str + lrs_str + ls_str
