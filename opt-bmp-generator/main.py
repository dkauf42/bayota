#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""

from util.castinputobj import CastInputObj
from util.geosuite import GeoSuite

#  MAIN FUNCTION  #
if __name__ == "__main__":

    geosuite = GeoSuite(optionsfile="../test/options_state_and_county.txt")

    print('<Loaded> Geo-objects: ')
    for g in geosuite.geoobjs:
        print(g)

    raise ValueError('<DONE>')

    # Create a County Object representing Anne Arundel
    #AACounty = County(name='Anne Arundel', srcdata=srcdata)

    # Create a State Object representing Maryland
    #MDState = State(name='MD', srcdata=srcdata)

    #print(AACounty)
    #print(AACounty.land_river_segments.head())
    #print(MDState)
    #print(MDState.land_river_segments.head())

    print(AACounty.land_river_segments.iloc[0])
    LSs = AACounty.loadsources_by_lrs(AACounty.land_river_segments.iloc[0])
    print(LSs)
    print(AACounty.countloadsources())

    castinput = CastInputObj()
    #castinput.create_landbmp_file()

