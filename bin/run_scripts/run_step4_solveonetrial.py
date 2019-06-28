#!/usr/bin/env python
"""
Note: No SLURM commands are submitted within this script.

Example usage command:
  >> ./bin/run_scripts/run_step4_solveonetrial.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step4_trial_control_2bd8452b-2560-48f6-8e36-a03cfa31e0e9.yaml
================================================================================
"""

import os
import sys
import subprocess
from argparse import ArgumentParser
import json

import pyomo.environ as pe

from bayota_util.spec_handler import read_spec, notdry
from bayom_e.src.solver_handling import solvehandler

from bayom_e.src.model_handling.utils import load_model_pickle

from bayota_settings.base import get_model_instances_dir, \
    get_output_dir, get_scripts_dir, get_logging_dir
from bayota_settings.log_setup import set_up_detailedfilelogger

logprefix = '** Single Trial **: '

move_to_s3_script = os.path.join(get_scripts_dir(), 'move_to_s3.py')
_S3BUCKET = 's3://modeling-data.chesapeakebay.net/'


def main(saved_model_file=None, model_modification_string=None, trial_name=None,
         control_file=None, solutions_folder_name=None,
         dryrun=False, translate_to_cast_format=False,
         move_solution_to_s3=False, move_CASTformatted_solution_to_s3=False,
         log_level='INFO') -> int:

    # The control file is read.
    if not not control_file:
        control_dict = read_spec(control_file)

        studyid = control_dict['study']['id']
        expid = control_dict['experiment']['id']

        model_modification_string = control_dict['trial']['modification'].lstrip('\'').rstrip('\'')

        trialidstr = control_dict['trial']['id']
        trial_name = control_dict['trial']['trial_name']
        saved_model_file = control_dict['model']['saved_file_for_this_study']
        solutions_folder_name = control_dict['trial']['solutions_folder_name']
        compact_geo_entity_str = control_dict['geography']['shortname']

        objective_and_constraint_str = control_dict['model']['objectiveshortname'] + '_' + \
                                       control_dict['model']['constraintshortname']

        # Control Options
        translate_to_cast_format = control_dict['control_options']['translate_solution_table_to_cast_format']
        s3_dict = control_dict['control_options']['move_files_to_s3']
        move_solution_to_s3 = bool(s3_dict['basic_solution'])
        move_CASTformatted_solution_to_s3 = bool(s3_dict['CASTformmated_solution'])
        s3_base_path = s3_dict['base_path_from_modeling-data']
    else:
        studyid = '0000'
        expid = '0000'
        trialidstr = '0000'
        compact_geo_entity_str = ''
        objective_and_constraint_str = ''
        s3_base_path = ''

    trial_logfilename = f"bayota_step4_s{studyid}_e{expid}_t{trialidstr}_{compact_geo_entity_str}"
    logger = set_up_detailedfilelogger(loggername=trial_name,  # same name as module, so logger is shared
                                       filename=trial_logfilename + '.log',
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)
    logger_feasibility = set_up_detailedfilelogger(loggername='feasibility',
                                                   filename='bayota_feasibility.log',
                                                   level='info',
                                                   also_logtoconsole=True,
                                                   add_filehandler_if_already_exists=False,
                                                   add_consolehandler_if_already_exists=False)

    # *****************************
    # Make Model Modification(s)
    # *****************************
    mdlhandler = load_model_pickle(savepath=saved_model_file, dryrun=dryrun, logprefix=logprefix)
    # Modification string is converted into a proper dictionary.
    modification_dict_withtrials = json.loads(model_modification_string)
    if not modification_dict_withtrials:
        modvar = None
        varvalue = None
    else:
        modvar, varvalue = make_model_modification(modification_dict_withtrials, dryrun, mdlhandler, logger)

    # *********************
    # Solve
    # *********************
    modelname_full = os.path.splitext(os.path.basename(saved_model_file))[0]
    notreal_notimestamp_outputdfpath = os.path.join(get_output_dir(), f"solution_{trial_name}_<timestamp>.csv")

    if notdry(dryrun, logger, f"--Dryrun-- Would run trial and save outputdf at: {notreal_notimestamp_outputdfpath}"):
        # The problem is solved.
        solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model,
                                                 translate_to_cast_format=translate_to_cast_format,
                                                 solverlogfile=os.path.join(get_logging_dir(), trial_logfilename + '_ipopt.log'))
        solution_dict['solution_df']['feasible'] = solution_dict['feasible']
        logger.info(f"Trial '{trial_name}' is DONE "
                    f"(@{solution_dict['timestamp']})! "
                    f"<Solution feasible? --> {solution_dict['feasible']}> ")
        logger_feasibility.info(f"<feasible: {solution_dict['feasible']}> for {modelname_full}_{trial_name}")

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
                logger.info('more than one objective found, only using one')
                break

        # Value of modified variable is added to the solution table.
        solution_dict['solution_df'][modvar] = varvalue
        # solution_dict['solution_df']['solution_mainconstraint_Percent_Reduction'] = pyo.value(mdlhandler.model.Percent_Reduction['N'].body)

        # Solution is saved.
        # Solutions directory is created if it doesn't exist.
        solutions_dir = os.path.join(get_output_dir(), solutions_folder_name)
        logger.debug(f"solutions_dir = {solutions_dir}")
        os.makedirs(solutions_dir, exist_ok=True)

        # Optimization solution table is written to file (uses comma-delimiter and .csv extention)
        solution_shortname = f"{trial_name}_{solution_dict['timestamp']}.csv"
        solution_fullname = f"{modelname_full}_{trial_name}_{solution_dict['timestamp']}.csv"

        outputdfpath_bayotaformat = os.path.join(solutions_dir, solution_fullname)
        solution_dict['solution_df'].to_csv(outputdfpath_bayotaformat)
        logger.info(f"<Solution written to: {outputdfpath_bayotaformat}>")

        s3_destination_dir = s3_base_path + compact_geo_entity_str + '/' + objective_and_constraint_str + '/'

        if move_solution_to_s3:
            # A shell command is built for this job submission.
            CMD = f"{move_to_s3_script} " \
                  f"-lp {outputdfpath_bayotaformat} " \
                  f"-dp {s3_destination_dir + solution_shortname} "

            # Job is submitted.
            logger.info(f'Job command is: "{CMD}"')
            if notdry(dryrun, logger, '--Dryrun-- Would submit command, then wait.'):
                p1 = subprocess.Popen([CMD], shell=True)
                p1.wait()
                # Get return code from process
                return_code = p1.returncode
                if p1.returncode != 0:
                    logger.error(f"Move-the-solution-to-s3 script exited with non-zero code <{return_code}>")
                    return 1

        # CAST-formatted solution table is written to file (uses tab-delimiter and .txt extention).
        if translate_to_cast_format:
            solution_shortname_castformat = f"castformat_{trial_name}_{solution_dict['timestamp']}.txt"
            solution_fullname_castformat = f"castformat_{modelname_full}_{trial_name}_{solution_dict['timestamp']}.txt"

            outputdfpath_castformat = os.path.join(solutions_dir, solution_fullname_castformat)
            # solution_dict['cast_formatted_df'].to_csv(outputdfpath,
            #                                           sep='\t', header=True, index=False, line_terminator='\r\n')

            with open(outputdfpath_castformat, 'wb') as dst:
                solution_dict['cast_formatted_df'].to_csv(outputdfpath_castformat,
                                                          sep='\t', header=True,
                                                          index=False, line_terminator='\r\n')
                dst.seek(-1, os.SEEK_END)  # <---- 1 : len('\n') to remove blank line at end of file
                dst.truncate()
            logger.info(f"<CAST-formatted solution written to: {outputdfpath_castformat}>")

            if move_CASTformatted_solution_to_s3:
                # A shell command is built for this job submission.
                CMD = f"{move_to_s3_script} " \
                      f"-lp {outputdfpath_castformat} " \
                      f"-dp {s3_destination_dir + solution_shortname_castformat} "

                # Job is submitted.
                logger.info(f'Job command is: "{CMD}"')
                if notdry(dryrun, logger, '--Dryrun-- Would submit command, then wait.'):
                    p1 = subprocess.Popen([CMD], shell=True)
                    p1.wait()
                    # Get return code from process
                    return_code = p1.returncode
                    if p1.returncode != 0:
                        logger.error(f"Move-the-cast-formatted-solution-to-s3 script exited with non-zero code <{return_code}>")
                        return 1

    return 0  # a clean, no-issue, exit


def make_model_modification(dictwithtrials, dryrun, mdlhandler, logger):
    varindexer = None

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

    return modvar, varvalue


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

    parser.add_argument("--no_s3", action='store_false',
                        help="don't move files to AWS S3 buckets")

    parser.add_argument("--translate_to_cast_format", action='store_true')

    parser.add_argument("-tn", "--trial_name", dest='trial_name',
                        help="unique name to identify this trial (used for saving results)")

    parser.add_argument("--solutions_folder_name", dest='solutions_folder_name',
                        help="the name of the folder to create and save the solution files to")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    opts = parser.parse_args()

    if not not opts.control_filepath:
        pass
    else:
        # MODEL SAVE FILE
        if not opts.saved_model_filepath:  # name was specified instead
            opts.saved_model_filepath = os.path.join(get_model_instances_dir(), opts.saved_model_name + '.yaml')

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
                  move_solution_to_s3=opts.no_s3,
                  move_CASTformatted_solution_to_s3=opts.no_s3,
                  translate_to_cast_format=opts.translate_to_cast_format,
                  log_level=opts.log_level))
