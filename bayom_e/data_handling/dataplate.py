""" Keep track of data for a particular kind of model
"""

# Generic/Built-in
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass, InitVar

# Computation
import pandas as pd

# BAYOTA
from bayota_util.str_manip import numstr


@dataclass
class NLP_DataPlate:
    """Class for keeping track of data for a particular kind of model.

    """

    # Sets
    PLTNTS: List[str]
    """ Example:
            ['N', 'P', 'S']
    """

    LRSEGS: List[str]
    """ Example:
            ['N42001PU0_3000_3090', 'N42001PU2_2790_3290', 'N42001PM2_2860_3040']
    """

    LOADSRCS: List[str]
    """ Example:
            ['aop', 'soy', 'gwm']
    """

    AGENCIES: Set[str]
    """ Example:
            {'dod', 'nonfed', 'nps'}
    """

    PARCELS: List[Tuple]
    """ Example:
            [('N42001PM3_3040_3340', 'aop', 'dod'),
             ('N42001PM3_3040_3340', 'soy', 'dod'),
             ('N42001PM3_3040_3340', 'gwm', 'dod')]
    """

    BMPS: List[str]
    """ Example:
            ['conplan',
             'advancedgi',
             'agstormeff']
    """

    BMPGRPS: List
    """ Example:
            [3, 13, 16]
    """

    BMPGRPING: Dict
    """ Example {BmpGroup:bmps} :
        {3: ['conplan'],
         13: ['septiceffadvanced', 'septicsecadvanced', 'septicdeadvanced'],
         16: ['agstormeff']}
    """

    BMPSRCLINKS: Dict
    """ Example  {LoadSource:bmps} :
        {'aop': ['conplan', 'watercontstruc', 'ditchfilter'],
         'cch': ['imperviousdisconnection'],
         'cci': ['imperviousdisconnection']}
    """

    BMPGRPSRCLINKS: Dict
    """ Example  {LoadSource:BmpGroups} :
        {'aop': [3, 41, 97],
         'cch': [42],
         'cci': [42]}
    """

    # Parameters
    theta: pd.DataFrame()  # target nutrient load (lb)
    alpha: pd.DataFrame()  # total acres of load source u (ac)
    phi: pd.DataFrame()  # load density of load source u (lb/ac)
    tau: pd.DataFrame()  # per acre cost of bmp b ($/ac)
    eta: pd.DataFrame()  # reduction effectiveness of bmp b when applied to load source u (% lb nutrient reduction)
    # self.totalcostupperbound = pd.DataFrame()

    def __repr__(self):
        obj_attributes = sorted([k for k in self.__dict__.keys()
                                 if not k.startswith('_')])

        strrep = f"DATAPLATE: \n" \
                 f"\t- includes <{len(self.LRSEGS)}> land river segments\n" \
                 f"\t- total area = {numstr(self.total_area(), 2)} acres (rounded to 2 decimal places)\n" \
                 f"\n" \
                 f"\t all attributes:%s" % '\n\t\t\t'.join(obj_attributes)

        return strrep

    def total_area(self):
        """ Get the total area (ac) of the LRsegs in this dataplate, from the 'alpha' attribute

        Returns:
            total area in acres (int)
        """
        return sum(self.alpha.values())
