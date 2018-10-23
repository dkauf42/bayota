import os
import pandas as pd
# import pyomo.environ as oe
import importlib

# from pyomo.util. import log_infeasible_constraints

from config.settings import get_graphics_path

from efficiencysubproblem.src.vis import sequence_plot
from efficiencysubproblem.src.vis.sequence_plot import plotlib_loadreductionobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

#%%
geoent = 'Northumberland, VA'
s = Study(objectivetype='loadreductionmax',
          geoscale='county', geoentities=[geoent])

countyname = geoent.split(',')[0]
stateabbrev = geoent.split(',')[1]

#%%
# mdl = s.modelhandler.model
# for l in mdl.LRSEGS:
#     for k in mdl.LOADSRCS:
#         print(mdl.T[l, k])
#
# print(sum((mdl.phi[l, lmbda, 'N'] * mdl.T[l, lmbda]) for lmbda in mdl.LOADSRCS))

#%%
(solver_output_filepaths,
 solution_csv_filepath,
 mdf,
 solution_objective,
 feasibility_list) = s.go_constraintsequence(list(range(0, 1000000, 100000)))

#%%
# log_infeasible_constraints(s.modelhandler.model)

#%%
constraintvar = 'totalcostupperbound'
df = pd.read_csv(solution_csv_filepath)
df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                           constraint_sequencing_var=constraintvar)

#%%
importlib.reload(sequence_plot)
from efficiencysubproblem.src.vis.sequence_plot import plotlib_loadreductionobj

fig = plotlib_loadreductionobj(df=df_piv, xname=constraintvar,
                      savefilepathandname=os.path.join(get_graphics_path(),
                                                       stateabbrev + countyname + '_totalcostbound1-1mil' + '_plotlibfig.png')
                      )
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


