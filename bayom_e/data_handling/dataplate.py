""" DATAPLATE class

"""
import pandas as pd
from dataclasses import dataclass, InitVar
from bayota_util.str_manip import numstr


@dataclass
class NLP_DataPlate:
    """Class for keeping track of data for a particular kind of model.

    """

    # Sets
    PLTNTS: pd.DataFrame()
    LRSEGS: pd.DataFrame()
    LOADSRCS: pd.DataFrame()
    AGENCIES: pd.DataFrame()
    PARCELS: pd.DataFrame()
    BMPS: pd.DataFrame()
    BMPGRPS: pd.DataFrame()
    BMPGRPING: pd.DataFrame()
    BMPSRCLINKS: pd.DataFrame()
    BMPGRPSRCLINKS: pd.DataFrame()

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
