import os

# from definitions import ROOT_DIR

# import pkg_resources
# access the filepath:
# ROOT_DIR = pkg_resources.resource_filename('root', 'config.txt')
from bayota_settings.install_config import get_graphics_dir
graphicsdir = get_graphics_dir()

from efficiencysubproblem.src.vis.sequence_plot import plotlib_costobj

from efficiencysubproblem.src.study import Study
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler

listofgeos = ['Allegany, MD',
              'Anne Arundel, MD',
              'Baltimore City, MD',
              'Calvert, MD',
              'Caroline, MD',
              'Carroll, MD',
              'Cecil, MD',
              'Charles, MD',
              'Dorchester, MD',
              'Frederick, MD',
              'Garrett, MD',
              'Harford, MD',
              'Howard, MD',
              'Kent, MD',
              'Montgomery, MD',
              'Prince Georges, MD',
              'Queen Annes, MD',
              'St. Marys, MD',
              'Baltimore, MD']


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
                          savefilepathandname=os.path.join(graphicsdir, 'graphics',
                                                           stateabbrev + countyname + '_tau1-10' + '_plotlibfig.png'),
                          secondaryxticklabels=df_piv['N_pounds_reduced'])
