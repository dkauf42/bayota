import os
import pandas as pd
from collections import OrderedDict
import pyomo.environ as oe
from pyomo.opt import SolverFactory, SolverManagerFactory
from amplpy import AMPL, Environment

from util.subproblem_model_loadobjective import LoadObj
from util.subproblem_model_costobjective import CostObj
from util.subproblem_solver_ipopt import SolveAndParse
from util.gjh_wrapper import gjh_solve, make_df
from vis.acres_bars import acres_bars
from vis.zL_bars import zL_bars

# %pylab inline
import seaborn as sns
import plotly.plotly as py
import plotly.graph_objs as go
from pandas.plotting import parallel_coordinates
from datetime import datetime

baseexppath = '/Users/Danny/Desktop/CATEGORIES/CAREER_MANAGEMENT/CRC_ResearchScientist_Optimization/Optimization_Tool/2_ExperimentFolder/'
projectpath = os.path.join(baseexppath, 'ampl/OptEfficiencySubProblem/')
amplappdir = os.path.join(baseexppath, 'ampl/amplide.macosx64/')

ampl = AMPL(Environment(amplappdir))
