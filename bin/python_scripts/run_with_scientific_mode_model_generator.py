import os
import cloudpickle
import pandas as pd
import pyomo.environ as pe
import importlib

# from pyomo.util. import log_infeasible_constraints

from efficiencysubproblem.src.vis import sequence_plot

from efficiencysubproblem.src.model_handling import model_generator
from efficiencysubproblem.src.spec_handler import read_spec

from efficiencysubproblem.src.solver_handling.solvehandler import solve_problem_instance
from efficiencysubproblem.src.solution_handling.solutionhandler import SolutionHandler
from bayota_settings.config_script import set_up_logger,\
    get_run_specs_dir, get_model_specs_dir, get_model_instances_dir, get_experiment_specs_dir, \
    get_output_dir

set_up_logger()
geo_spec_file = os.path.join(get_run_specs_dir(), 'geography_specs.yaml')
savepath = os.path.join(get_model_instances_dir(), 'saved_instance.pickle')
exp_spec_file = os.path.join(get_experiment_specs_dir(), 'costmin_1-10percentreduction_noUrbanNMPlanHR.yaml')


#%% Model Generation
geography_name = 'CalvertMD'
geodict = read_spec(geo_spec_file)[geography_name]

# model_spec_file = os.path.join(get_model_specs_dir(), 'loadreductionmax.yaml')
model_spec_file = os.path.join(get_model_specs_dir(), 'costmin_total_percentreduction.yaml')
mdlhandler = model_generator.ModelHandlerBase(model_spec_file=model_spec_file,
                                              geoscale=geodict['scale'],
                                              geoentities=geodict['entities'],
                                              savedata2file=False)


#%% Experiment Setup
# from efficiencysubproblem.src.model_handling import utils
# importlib.reload(utils)
#
# actionlist=read_spec(exp_spec_file)['exp_setup']
# for a in actionlist:
#     try:
#         if a['name'] == 'p_ub':
#             continue
#     except KeyError:
#         pass
#     utils.modify_model(mdlhandler.model, actiondict=a)
#
#
# mdlhandler.model.component('totalcostupperbound').pprint()

#%% Save the model
with open(savepath, 'wb') as f:
    cloudpickle.dump(mdlhandler, f)


#%% Load the model
with open(savepath, 'rb') as f:
    mdlhandler = cloudpickle.load(f)

#%%
# mdlhandler.model.x['UrbanNMPlanHR', :, :].pprint()

# from IPython import display
#%%
from efficiencysubproblem.src.solver_handling import solvehandler
importlib.reload(solvehandler)
from efficiencysubproblem.src.solver_handling import solvehandler

experiment_spec_file = os.path.join(get_experiment_specs_dir(), 'costmin_1-20percentreduction.yaml')
# experiment_spec_file = os.path.join(get_experiment_specs_dir(), 'loadreductionmax_100000-1mil_total_cost_bound.yaml')


# Log the list of trial sets that will be conducted for this experiment
list_of_trialdicts = read_spec(experiment_spec_file)['trials']
tempstr = 'set' if len(list_of_trialdicts) == 1 else 'sets'
print(f"trial {tempstr} to be conducted: {list_of_trialdicts}")

# Loop through and start each trial
trialnum = 0
for i, dictwithtrials in enumerate(list_of_trialdicts):
    print(f'trial set #{i}: {dictwithtrials}')

    modvar = dictwithtrials['variable']
    print(f'variable to modify: {modvar}')

    varvalue = dictwithtrials['value']
    print('values: %s' % varvalue)

    varindexer = None
    try:
        varindexer = dictwithtrials['indexer']
        print(f'indexed over: {varindexer}')
    except KeyError:
        pass

    for vi in varvalue:
        trialnum += 1
        trialstr = '{:04}'.format(trialnum)

        print(f'trial #{trialstr}, setting <{modvar}> to <{vi}>')
        if not varindexer:
            print('not using varindexer')
            setattr(mdlhandler.model, modvar, vi)
        else:
            print('using varindexer')
            print(modvar)
            mdlhandler.model.component(modvar)[varindexer] = vi


        solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model, )
        print(f"Trial '{trialstr}' is DONE "
              f"(@{solution_dict['timestamp']})! "
              f"<Solution feasible? --> {solution_dict['feasible']}> ")

        solution_dict['solution_df']['feasible'] = solution_dict['feasible']

        ii = 0
        for c in mdlhandler.model.component_objects(pe.Objective):
            if ii < 1:
                solution_dict['solution_df']['solution_objective'] = pe.value(getattr(mdlhandler.model, str(c)))
                ii += 1
            else:
                print('more than one objective found, only using one')
                break

        solution_dict['solution_df'][modvar] = vi
        solution_dict['solution_df']['solution_mainconstraint_Percent_Reduction'] = pe.value(mdlhandler.model.Percent_Reduction['N'].body)

        outputdfpath = os.path.join(get_output_dir(), f"solutiondf_{trialstr}_{solution_dict['timestamp']}.csv")
        solution_dict['solution_df'].to_csv(outputdfpath)
        print(f"<Solution written to: {outputdfpath}>")

#%%

ii=0
for c in mdlhandler.model.component_objects(pe.Objective):
    if ii > 0:
        break
    print(c)  # Prints the name of every Objective on the model
    print(pe.value(getattr(mdlhandler.model, str(c))))
    ii += 1

for c in mdlhandler.model.component_objects(pe.Constraint):
    print(c)
# print(pe.value(mdlhandler.model.Percent_Reduction['N'].body))

#%%
# print constraint
mdlhandler.model.component('Percent_Reduction').pprint()

#%%

#%% Problem Solving
solution = solve_problem_instance(mdlbase, mdl, randomstart=False, output_file_str='', fileprintlevel=4)

#%%
print(solution)
#%%

# WITH ARGUMENTS
# lrsegs_for_annearundel = ['N24003WM0_3966_0000'] #['N24003WL0_4390_0000', 'N24003WL0_4424_0000', 'N24003WL0_4601_0000', 'N24003WL0_4393_0000']  #['N24003XU3_4650_0001', 'N24003XU2_4480_4650', 'N24003XL3_4710_0000', 'N24003XL3_4711_0000', 'N24003XL3_4712_0000', 'N24003XL3_4713_0000', 'N24003XL3_4950_0000', 'N24003XU2_4270_4650', 'N24003WL0_4420_0000', 'N24003WL0_4421_0000', 'N24003WL0_4422_0000', 'N24003WL0_4423_0000', 'N24003WL0_4600_0000', 'N24003WL0_4602_0000', 'N24003WL0_4603_0000', 'N24003WL0_4770_0000', 'N24003WL0_4771_0000', 'N24003WL0_4772_0000', 'N24003WM0_3961_0000', 'N24003WM0_3962_0000', 'N24003WM0_3963_0000', 'N24003WM3_4060_0001', 'N24003WL0_4425_0000', 'N24003WL0_4394_0000', 'N24003WL0_4391_0000', 'N24003WL0_4392_0000']
geoent = 'N42001PU0_3000_3090'
s = Study(objectivetype='costmin',
          geoscale='lrseg', geoentities=[geoent]) #[geoent]) #lrsegs_for_annearundel)  #[geoent])

# WITH CONFIG FILE
# from pathlib import Path
#
# configpath = Path('__file__').absolute().parent/'bin'/'studies'/'study_a1_mdcounties.ini'
# s = Study(configfile=configpath) #[geoent]) #lrsegs_for_annearundel)  #[geoent])


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
feasibility_list) = s.go_constraintsequence(list(np.arange(1, 3)))
# feasibility_list) = s.go_constraintsequence(list(np.arange(0.01, 0.1, 0.01)))
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


