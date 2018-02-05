import pandas as pd
from tqdm import tqdm  # Loop progress indicator module


class Constraints:
    def __init__(self, sourcedataobj=None, optionloaderobj=None, baseconditionobj=None):
        """Determine the mins and maxes for each BMP"""

        """ Get Pre-BMP acres for each agricultural lrseg-agency-type (from PreBmpLoadSourceAgriculture table
                                                                         or Base Condition table) """
        # This will be an upper bound for certain efficiency and load reduction BMP groups

        """ Get Pre-BMP acres for each developed lrseg-agency-type (from PreBmpLoadSourceDeveloped table
                                                                      or Base Condition table) """
        # This will be an upper bound for certain efficiency and load reduction BMP groups

        """ Get Pre-BMP acres for each acreage-based natural lrseg-agency-type (from PreBmpLoadSourceNatural table
                                                                                  or Base Condition table) """
        # This will be an upper bound for
        # - CSS Mixed Open
        # - CSS Forest
        # - Harvested Forest
        # - True Forest
        # - Non-tidal Floodplain Wetland
        # - Headwater or Isolated Wetland
        # - Mixed Open
        # - Water

        """ Get Pre-BMP miles for each mileage-based natural lrseg-agency-type (from PreBmpLoadSourceNatural table
                                                                                  or Base Condition table) """
        # This will be an upper bound for
        # - Stream Flood Plain
        # - Shoreline
        # - Stream Bed and Bank

        """ Get Pre-BMP Amounts for each lrseg-agency-septic (from SepticSystems table) """
        # This will be an upper bound for
        # - Septic

        """ Get Animal Counts (from AnimalPopulation table) """
        # This will be an upper bound for certain animal BMPs


        # Mutually Inclusive ("overlapping", "multiplicative")
        # {There are separate, multiplicative BMP groups.}

        # Mutually Exclusive ("non-overlapping", "additive", e.g. forest and grass buffers)
        # {These are considered within a multiplicative BMP group.}