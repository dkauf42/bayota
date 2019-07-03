import pandas as pd
from dataclasses import dataclass, InitVar


@dataclass
class NLP_DataPlate:
    """Class for keeping track of data for a particular kind of model.


    """

    # Sets
    PLTNTS: pd.DataFrame()
    LRSEGS: pd.DataFrame()
    BMPS: pd.DataFrame()
    BMPGRPS: pd.DataFrame()
    BMPGRPING: pd.DataFrame()
    LOADSRCS: pd.DataFrame()
    BMPSRCLINKS: pd.DataFrame()
    BMPGRPSRCLINKS: pd.DataFrame()

    # Parameters
    theta: pd.DataFrame()  # target nutrient load (lb)
    alpha: pd.DataFrame()  # total acres of load source u (ac)
    phi: pd.DataFrame()  # load density of load source u (lb/ac)
    tau: pd.DataFrame()  # per acre cost of bmp b ($/ac)
    eta: pd.DataFrame()  # reduction effectiveness of bmp b when applied to load source u (% lb nutrient reduction)
    # self.totalcostupperbound = pd.DataFrame()

    # database: InitVar[] = None

    # def __post_init__(self, database):
    #     if self.j is None and database is not None:
    #         self.j = database.lookup('j')

    #
    # name: str
    # unit_price: float
    # quantity_on_hand: int = 0

    # def total_cost(self) -> float:
    #     return self.unit_price * self.quantity_on_hand