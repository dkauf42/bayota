""" Keep track of data for a particular kind of model
"""

# Generic/Built-in
import types
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

    def equals(self, other):
        def dict_compare(d1, d2):
            d1_keys = set(d1.keys())
            d2_keys = set(d2.keys())
            shared_keys = d1_keys.intersection(d2_keys)
            added = d1_keys - d2_keys
            removed = d2_keys - d1_keys
            modified = {o: (d1[o], d2[o]) for o in shared_keys if d1[o] != d2[o]}
            same = set(o for o in shared_keys if d1[o] == d2[o])
            return added, removed, modified, same

        for i, att in enumerate([a for a in dir(self) if not a.startswith('__')]):
            print(f"**{att}**")
            att1 = getattr(self, att)
            att2 = getattr(other, att)

            if att == 'theta':
                print("  skipping theta because it can be undefined.")
                continue

            msg = ""
            if isinstance(att1, dict):
                added, removed, modified, same = dict_compare(att1, att2)
                if len(added) != 0:
                    msg += f"added = {added}\n"
                if len(removed) != 0:
                    msg += f"removed = {removed}\n"
                if len(modified) != 0:
                    msg += f"modified = {modified}\n"

            elif isinstance(att1, set):
                difference_set = att1.symmetric_difference(att2)
                if len(difference_set) != 0:
                    msg += f"differences = {difference_set}\n"

            elif isinstance(att1, list):
                if att1 != att2:
                    msg += f"differences (n - d) = {att2 - att1}\n"
                    msg += f"differences (d - n) = {att2 - att1}\n"

            elif isinstance(att1, pd.DataFrame):
                if att1.empty:
                    msg += f"Dataframe 1 is empty!\n"
                if att2.empty:
                    msg += f"Dataframe 2 is empty!\n"
                if (not msg) & (not att1.equals(att2)):
                    msg += f"Dataframes are not equal!\n"

            elif isinstance(att1, types.MethodType):
                print("  skipping this because it is an instance method.")
                continue

            else:
                print(f'-- unexpected type! --, {type(att1)}')
                continue

            if msg:
                print(msg)
            else:
                print("  no differences :)")

    def total_area(self):
        """ Get the total area (ac) of the LRsegs in this dataplate, from the 'alpha' attribute

        Returns:
            total area in acres (int)
        """
        return sum(self.alpha.values())
