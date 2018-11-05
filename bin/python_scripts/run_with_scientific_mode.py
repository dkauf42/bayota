import os
import pandas as pd
# import pyomo.environ as oe
import importlib

# from pyomo.util. import log_infeasible_constraints

from bayota_settings.install_config import get_graphics_dir

from efficiencysubproblem.src.vis import sequence_plot
from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

graphicsdir = get_graphics_dir()

#%%

# WITH ARGUMENTS
# lrsegs_for_annearundel = ['N24003WM0_3966_0000'] #['N24003WL0_4390_0000', 'N24003WL0_4424_0000', 'N24003WL0_4601_0000', 'N24003WL0_4393_0000']  #['N24003XU3_4650_0001', 'N24003XU2_4480_4650', 'N24003XL3_4710_0000', 'N24003XL3_4711_0000', 'N24003XL3_4712_0000', 'N24003XL3_4713_0000', 'N24003XL3_4950_0000', 'N24003XU2_4270_4650', 'N24003WL0_4420_0000', 'N24003WL0_4421_0000', 'N24003WL0_4422_0000', 'N24003WL0_4423_0000', 'N24003WL0_4600_0000', 'N24003WL0_4602_0000', 'N24003WL0_4603_0000', 'N24003WL0_4770_0000', 'N24003WL0_4771_0000', 'N24003WL0_4772_0000', 'N24003WM0_3961_0000', 'N24003WM0_3962_0000', 'N24003WM0_3963_0000', 'N24003WM3_4060_0001', 'N24003WL0_4425_0000', 'N24003WL0_4394_0000', 'N24003WL0_4391_0000', 'N24003WL0_4392_0000']
# # geoent = 'Anne Arundel, MD'
# s = Study(objectivetype='costmin',
#           geoscale='lrseg', geoentities=lrsegs_for_annearundel) #[geoent]) #lrsegs_for_annearundel)  #[geoent])

# WITH CONFIG FILE
from pathlib import Path

configpath = Path('__file__').absolute().parent/'bin'/'studies'/'study_a1_mdcounties.ini'
s = Study(configfile=configpath) #[geoent]) #lrsegs_for_annearundel)  #[geoent])

# countyname = geoent.split(',')[0]
# stateabbrev = geoent.split(',')[1]

#%%
# mdl = s.modelhandler.model
# for l in mdl.LRSEGS:
#     for k in mdl.LOADSRCS:
#         print(mdl.T[l, k])
#
# print(sum((mdl.phi[l, lmbda, 'N'] * mdl.T[l, lmbda]) for lmbda in mdl.LOADSRCS))

#%%
import pyomo.environ as oe
s.modelhandler.model.phi.pprint()

# for s.modelhandler.model.component(x)

#%%
import numpy as np
(solver_output_filepaths,
 solution_csv_filepath,
 mdf,
 solution_objective,
feasibility_list) = s.go_constraintsequence(list(np.arange(0.01, 0.1, 0.01)))
 # feasibility_list) = s.go_constraintsequence(list(range(0, 5000000, 1000000)))

#%%
# log_infeasible_constraints(s.modelhandler.model)

#%%
constraintvar = 'tau'
df = pd.read_csv(solution_csv_filepath)
df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                           constraint_sequencing_var=constraintvar)

#%%
importlib.reload(sequence_plot)
from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

fig = plotlib_costobj(df=df_piv, xname=constraintvar,
                          savefilepathandname=os.path.join(graphicsdir,
                                                           stateabbrev + countyname + '_' + constraintvar + '1-10' + '_plotlibfig.png'),
                      backend=None)
                      #secondaryxticklabels=df_piv['N_pounds_reduced'])
# py.iplot(fig, filename='styled-line')

#%%
# jeeves = Jeeves()
#%%
df_single = df[df['tau']==9].copy()
cast_input_df = SolutionHandler().make_cast_input_table_from_solution(df_single)

#%%
#
# newtable = df_single.copy()
#
# # Get relevant source data tables
# TblLandRiverSegment = jeeves.source.TblLandRiverSegment
# TblState = jeeves.source.TblState
# TblAgency = jeeves.source.TblAgency
# TblLoadSource = jeeves.source.TblLoadSource
# TblBmp = jeeves.source.TblBmp
#
# #%%
# # add stateid
# columnmask = ['landriversegment', 'stateid']
# newtable = TblLandRiverSegment.loc[:, columnmask].merge(newtable, how='inner')


