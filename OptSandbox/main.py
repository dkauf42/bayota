#!/usr/bin/env python

"""
Test various BMP-load source combinations
"""
import sys
import os
import timeit
from util.Runner import Runner

script_dir = os.path.dirname(os.path.realpath(__file__))  # <-- absolute dir of this script
sys.path.append(script_dir)


def main():
    start_time = timeit.default_timer()
    # A scenario is generated from options, and possibility matrices are generated.
    Runner(optionsfile="../test/options_AAcounty.txt")
    print("Loading time", timeit.default_timer() - start_time)
    print('<DONE>')


if __name__ == '__main__':
    main()
