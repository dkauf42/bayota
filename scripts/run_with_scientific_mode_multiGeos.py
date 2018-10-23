
import os
import pandas as pd

# from definitions import ROOT_DIR

import pkg_resources
# access the filepath:
ROOT_DIR = pkg_resources.resource_filename('root', 'config.txt')

from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

#%%
# listofgeos = ['Hampshire, WV',
#               'Broome, NY',
#               'Cumberland, PA',
#               'Wicomico, MD',
#               'Nelson, VA',
#               'Kent, DE',
#               'District of Columbia, DC',
#               'Calvert, MD',
#               'Montgomery, MD'
#               'Adams, PA',
#               'Sussex, DE',
#               'Jefferson, WV',
#               'Dorchester, MD',
#               'Centre, PA',
#               'Steuben, NY',
#               'Northumberland, VA',
#               'Botetourt, VA',
#               'Fairfax, VA',
#               'Anne Arundel, MD']

listofgeos = ['Allegany, MD'
              'Anne Arundel, MD'
              'Baltimore, MD'
              'Baltimore City, MD'
              'Calvert, MD'
              'Caroline, MD'
              'Carroll, MD'
              'Cecil, MD'
              'Charles, MD'
              'Dorchester, MD'
              'Frederick, MD'
              'Garrett, MD'
              'Harford, MD'
              'Howard, MD'
              'Kent, MD'
              'Montgomery, MD'
              'Prince Georges, MD'
              'Queen Annes, MD'
              'St. Marys, MD']

#%%

for g in listofgeos:
    print(g)
    s = Study(objectivetype='costmin',
              geoscale='county', geoentities=[g],
              baseconstraint=3)

    countyname = g.split(',')[0]
    stateabbrev = g.split(',')[1]

    # (solver_output_filepaths,
    #  solution_csv_filepath,
    #  mdf,
    #  solution_objective) = s.go(5)

    (solver_output_filepaths,
     solution_csv_filepath,
     mdf,
     solution_objective,
     feasibility_list) = s.go_constraintsequence(range(1, 11))

    constraintvar = 'tau'
    df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                               constraint_sequencing_var=constraintvar)

    fig = plotlib_costobj(df=df_piv, xname=constraintvar,
                          savefilepathandname=os.path.join(ROOT_DIR,
                                                           stateabbrev + countyname + '_graphics_tau1-10' + '_plotlyfig.png'))
    # py.iplot(fig, filename='styled-line')

#%%
mdl = s.modelhandler.model
for l in mdl.LRSEGS:
    for k in mdl.LOADSRCS:
        print(mdl.T[l, k])

print(sum((mdl.phi[l, lmbda, 'N'] * mdl.T[l, lmbda]) for lmbda in mdl.LOADSRCS))

#%%
solver_output_filepaths,\
solution_csv_filepath, \
mdf, \
solution_objective = s.go_constraintsequence(range(9, 10))

#%%
constraintvar = 'tau'
df = pd.read_csv(solution_csv_filepath)
df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                           constraint_sequencing_var=constraintvar)

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


