#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import timeit
import sys
import os

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)

from util.InputsToCast import InputsToCast
from util.Scenario import Scenario

#  MAIN FUNCTION  #
#if __name__ == "__main__":
#    pass
#else:

start_time = timeit.default_timer()
# A suite of Geo objects, specified in the options file, is loaded.
scenario = Scenario(optionsfile="../test/options_AAcounty.txt")
print("Loading time", timeit.default_timer() - start_time)
#for g in geosuite.geoobjs:
#    print(g)

raise ValueError('<DONE>')
print(AACounty.land_river_segments.iloc[0])
LSs = AACounty.loadsources_by_lrs(AACounty.land_river_segments.iloc[0])
print(LSs)
print(AACounty.countloadsources())
castinput = CastInputObj()
#castinput.create_landbmp_file()

