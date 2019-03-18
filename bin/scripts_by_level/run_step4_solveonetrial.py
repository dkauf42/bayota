#!/usr/bin/env python

"""
Example usage command:

"""
import os
import sys
import logging
import subprocess
from argparse import ArgumentParser
import json

import pyomo.environ as pe

from efficiencysubproblem.src.spec_handler import read_spec, notdry
from efficiencysubproblem.src.solver_handling import solvehandler

from efficiencysubproblem.src.model_handling.utils import load_model_pickle

from bayota_settings.config_script import set_up_logger, get_model_instances_dir, \
    get_output_dir, get_scripts_dir

logger = logging.getLogger('root')
if not logger.hasHandlers():
    set_up_logger()
    logger = logging.getLogger(__name__)

move_to_s3_script = os.path.join(get_scripts_dir(), 'move_to_s3.py')
_S3BUCKET = 's3://modeling-data.chesapeakebay.net/'


def main(saved_model_file=None, model_modification_string=None, trial_name=None,
         control_file=None, solutions_folder_name=None,
         dryrun=False, no_s3=False, no_slurm=False, translate_to_cast_format=False):
    logprefix = '** Single Trial **: '

    # Read the trial control file
    if not not control_file:
        control_dict = read_spec(control_file)

        # convert modification string into a proper dictionary
        model_modification_string = control_dict['trial']['modification'].lstrip('\'').rstrip('\'')

        trial_name = control_dict['trial']['trial_name']
        saved_model_file = control_dict['model']['saved_file_for_this_study']
        solutions_folder_name = control_dict['trial']['solutions_folder_name']

        geography_entity_str = control_dict['geography']['entity'].replace(' ', '').replace(',', '')
        objective_and_constraint_str = control_dict['model']['objectiveshortname'] + '_' + \
                                       control_dict['model']['constraintshortname']

        # Control Options
        no_s3 = not bool(control_dict['control_options']['move_solution_to_s3'])
        translate_to_cast_format = control_dict['control_options']['translate_solution_table_to_cast_format']
    else:
        geography_entity_str = ''
        objective_and_constraint_str = ''

    # convert modification string into a proper dictionary
    dictwithtrials = json.loads(model_modification_string)

    mdlhandler = load_model_pickle(savepath=saved_model_file, dryrun=dryrun, logprefix=logprefix)

    modvar = None
    varvalue = None
    varindexer = None

    # *********************
    # Make Modification
    # *********************
    if not not dictwithtrials:
        modvar = dictwithtrials['variable']
        varvalue = dictwithtrials['value']

        try:
            varindexer = dictwithtrials['indexer']
            print(f'indexed over: {varindexer}')
        except KeyError:
            pass

        if not varindexer or (varindexer == 'None'):
            if notdry(dryrun, logger, '--Dryrun-- Would make model modification; '
                                      'setting %s to %s (no index)' %
                                      (modvar, varvalue)):
                setattr(mdlhandler.model, modvar, varvalue)
        else:
            if notdry(dryrun, logger, '--Dryrun-- Would make model modification; '
                                      'setting %s to %s (at index %s)' %
                                      (modvar, varvalue, varindexer)):
                mdlhandler.model.component(modvar)[varindexer] = varvalue

    # *********************
    # Solve
    # *********************
    modelname_full = os.path.splitext(os.path.basename(saved_model_file))[0]
    notreal_notimestamp_outputdfpath = os.path.join(get_output_dir(),
                                                    f"solution_{trial_name}_<timestamp>.csv")

    if notdry(dryrun, logger, f"--Dryrun-- Would run trial and save outputdf at: {notreal_notimestamp_outputdfpath}"):

        # The problem is solved.
        solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model,
                                                 translate_to_cast_format=translate_to_cast_format)
        solution_dict['solution_df']['feasible'] = solution_dict['feasible']
        logger.info(f"{logprefix} Trial '{trial_name}' is DONE "
                    f"(@{solution_dict['timestamp']})! "
                    f"<Solution feasible? --> {solution_dict['feasible']}> ")

        # Optimization objective value is added to the solution table.
        ii = 0
        for objective_component in mdlhandler.model.component_objects(pe.Objective):
            if ii < 1:
                # check whether Objective is an "indexed" component or not
                if objective_component._index == {None}:
                    solution_dict['solution_df']['solution_objective'] = pe.value(objective_component)
                else:
                    for cidxpart in objective_component:
                        if objective_component[cidxpart].active:
                            solution_dict['solution_df']['solution_objective'] = pe.value(objective_component[cidxpart])

                ii += 1
            else:
                print('more than one objective found, only using one')
                break

        # Value of modified variable is added to the solution table.
        solution_dict['solution_df'][modvar] = varvalue
        # solution_dict['solution_df']['solution_mainconstraint_Percent_Reduction'] = pe.value(mdlhandler.model.Percent_Reduction['N'].body)

        # Solution is saved.
        # Solutions directory is created if it doesn't exist.
        solutions_dir = os.path.join(get_output_dir(), solutions_folder_name)
        logger.debug(f"solutions_dir = {solutions_dir}")
        os.makedirs(solutions_dir, exist_ok=True)

        # CAST-formatted solution table is written to file (uses tab-delimiter and .txt extention).
        if translate_to_cast_format:
            solution_name = f"castformat_{trial_name}_{solution_dict['timestamp']}.txt"
            outputdfpath_castformat = os.path.join(solutions_dir, solution_name)
            # solution_dict['cast_formatted_df'].to_csv(outputdfpath,
            #                                           sep='\t', header=True, index=False, line_terminator='\r\n')

            with open(outputdfpath_castformat, 'wb') as dst:
                solution_dict['cast_formatted_df'].to_csv(outputdfpath_castformat,
                                                          sep='\t', header=True,
                                                          index=False, line_terminator='\r\n')
                dst.seek(-1, os.SEEK_END)  # <---- 1 : len('\n') to remove blank line at end of file
                dst.truncate()

            logger.info(f"<CAST-formatted solution written to: {outputdfpath_castformat}>")

        # Optimization info solution table is written to file (uses comma-delimiter and .csv extention)
        solution_name = f"{trial_name}_{solution_dict['timestamp']}.csv"
        outputdfpath_bayotaformat = os.path.join(solutions_dir, solution_name)
        solution_dict['solution_df'].to_csv(outputdfpath_bayotaformat)
        logger.info(f"<Solution written to: {outputdfpath_bayotaformat}>")

        if no_s3:
            pass
        else:
            # Move solution file to s3
            destination_name = 'optimization' + '/' \
                               + 'for_kevin_20190318' + '/' \
                               + geography_entity_str + '/' \
                               + objective_and_constraint_str + '/' \
                               + solution_name

            # Create a job to submit to the queue
            CMD = f"{move_to_s3_script} " \
                  f"-op {outputdfpath_bayotaformat} " \
                  f"-dp {destination_name} "
            if not no_slurm:
                CMD = "srun " + CMD
            else:
                pass

            # Submit the job
            logger.info(f'Job command is: "{CMD}"')
            p1 = None
            if notdry(dryrun, logger, '--Dryrun-- Would submit command'):
                p1 = subprocess.Popen([CMD], shell=True)
            if notdry(dryrun, logger, '--Dryrun-- Would wait'):
                p1.wait()


def parse_cli_arguments():
    # Input arguments are parsed.
    parser = ArgumentParser()

    # Arguments for top-level
    one_or_the_other = parser.add_mutually_exclusive_group()
    one_or_the_other.add_argument("-sn", "--saved_model_name", dest="saved_model_name",
                                            help="name for the saved (pickled) model file")
    one_or_the_other.add_argument("-sf", "--saved_model_filepath", dest="saved_model_filepath",
                                            help="path for the saved (pickled) model file")
    one_or_the_other.add_argument("-cf", "--control_filepath", dest="control_filepath", default=None,
                                  help="path for this study's control file")

    parser.add_argument("-m", "--model_modification_string", dest='model_modification_string',
                        help="modifications to be made to the model after loading and before solving trial instance")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--no_s3", action='store_true',
                        help="don't move files to AWS S3 buckets")

    parser.add_argument("--no_slurm", action='store_true',
                        help="don't use AWS or slurm facilities")

    parser.add_argument("--translate_to_cast_format", action='store_true')

    parser.add_argument("-tn", "--trial_name", dest='trial_name',
                        help="unique name to identify this trial (used for saving results)")

    parser.add_argument("--solutions_folder_name", dest='solutions_folder_name',
                        help="the name of the folder to create and save the solution files to")

    parser.add_argument("-v", "--verbose", dest='verbose',
                        action="count", default=0)

    opts = parser.parse_args()

    if not not opts.control_filepath:
        pass
    else:
        # MODEL SAVE FILE
        if not opts.saved_model_filepath:  # name was specified instead
            opts.saved_model_filepath = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')

    print(opts)
    return opts


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(saved_model_file=opts.saved_model_filepath,
                  model_modification_string=opts.model_modification_string,
                  control_file=opts.control_filepath,
                  trial_name=opts.trial_name,
                  solutions_folder_name=opts.solutions_folder_name,
                  dryrun=opts.dryrun,
                  no_s3=opts.no_s3,
                  no_slurm=opts.no_slurm,
                  translate_to_cast_format=opts.translate_to_cast_format))
