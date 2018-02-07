#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import sys
import os
import timeit
from util.Scenario import Scenario
import util.conf

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main():
    start_time = timeit.default_timer()
    # A scenario is generated from options, and possibility matrices are generated.
    Scenario(optionsfile="../test/options_AAcounty.txt")
    print("Loading time", timeit.default_timer() - start_time)
    print('<DONE>')


if __name__ == '__main__':
    util.conf.init(sys.argv[1:])
    if util.conf.DEBUG:
        print('debug is on')
    main()
