#!/usr/bin/env python
import yaml
from argparse import ArgumentParser


def read_spec(spec_file):
    adict = None
    with open(spec_file, 'r') as stream:
        try:
            adict = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    return adict


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser()
    one_or_the_other = parser.add_mutually_exclusive_group(required=True)
    one_or_the_other.add_argument("-s", "--study_spec", dest="study_spec_file", default=None,
                                  help="read_spec in a study specification file")
    one_or_the_other.add_argument("-e", "--experiment_spec", dest="experiment_spec_file", default=None,
                                  help="read_spec in an experiment specification file")
    opts = parser.parse_args()

    if not opts.experiment_spec_file:  # study spec was given
        opts.specfile = opts.study_spec_file
    else:  # experiment spec was given
        opts.specfile = opts.experiment_spec_file

    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    adict = read_spec(opts.specfile)

    print(adict)
