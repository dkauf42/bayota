import os

from definitions import ROOT_DIR

from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

listofgeos = ['Hampshire, WV',
              'Broome, NY',
              'Cumberland, PA',
              'Wicomico, MD',
              'Nelson, VA',
              'Kent, DE',
              'District of Columbia, DC',
              'Calvert, MD',
              'Montgomery, MD',
              'Adams, PA',
              'Sussex, DE',
              'Jefferson, WV',
              'Dorchester, MD',
              'Centre, PA',
              'Steuben, NY',
              'Northumberland, VA',
              'Botetourt, VA',
              'Fairfax, VA',
              'Anne Arundel, MD']


for g in listofgeos:
    print(g)
    s = Study(objectivetype='costmin',
              geoscale='county', geoentities=[g])

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
     feasibility_list) = s.go_constraintsequence(range(1, 16))

    constraintvar = 'tau'
    df_piv = SolutionHandler.make_pivot_from_solution_sequence(solution_csv_filepath=solution_csv_filepath,
                                                               constraint_sequencing_var=constraintvar)

    fig = plotlib_costobj(df=df_piv, xname=constraintvar,
                          savefilepathandname=os.path.join(ROOT_DIR, 'graphics',
                                                           stateabbrev + countyname + '_tau1-10' + '_plotlibfig.png'),
                          secondaryxticklabels=df_piv['N_pounds_reduced'])
