#!/usr/bin/env python
"""
Note: No SLURM commands are submitted within this script.

Example usage command:
  >> ./bin/run_steps/step3_solveonetrial.py --dryrun -cf ~/bayota_ws_0.1a1.dev4/control/step4_trial_control_2bd8452b-2560-48f6-8e36-a03cfa31e0e9.yaml
================================================================================
"""

import os
import sys
import datetime
from argparse import ArgumentParser
import json

import pyomo.environ as pyo

from bayota_util.spec_and_control_handler import notdry, read_trialcon_file, \
    read_control, write_progress_file, get_control_dir
from bayota_util.s3_operations import establish_s3_connection, pull_workspace_subdir_from_s3, \
    pull_model_instance_from_s3
from bayom_e.solver_handling.solvehandler import SolveHandler
from bayom_e.solution_handling.ipopt_parser import IpoptParser

from bayom_e.model_handling.utils import load_model_pickle

from bayota_settings.base import get_output_dir, get_logging_dir
from bayota_settings.log_setup import set_up_detailedfilelogger

logprefix = '** Single Trial **: '


def main(control_file, dryrun=False, use_s3_ws=False, save_to_s3=False, log_level='INFO') -> int:
    if save_to_s3 or use_s3_ws:
        # Connection with S3 is established.
        s3ops = establish_s3_connection(log_level, logger=None)

    # If using s3, required workspace directories are pulled from buckets.
    if use_s3_ws:
        pull_workspace_subdir_from_s3(subdirname='control', s3ops=s3ops, log_level=log_level)
        pull_workspace_subdir_from_s3(subdirname='data', s3ops=s3ops, log_level=log_level)
        pull_workspace_subdir_from_s3(subdirname='specfiles', s3ops=s3ops, log_level=log_level)

    # Control file is read.
    control_dict, \
    compact_geo_entity_str, \
    expid, \
    model_modification_string, \
    move_CASTformatted_solution_to_s3, \
    move_solution_to_s3, \
    objective_and_constraint_str, \
    s3_base_path, \
    saved_model_name, \
    saved_model_file, \
    solutions_folder_name, \
    studyid, \
    studyshortname, \
    translate_to_cast_format, \
    trial_name, \
    trialidstr = read_trialcon_file(control_file_name=control_file)

    # Logging formats are set up.
    trial_logfilename = f"bayota_step4_s{studyid}_e{expid}_t{trialidstr}_{compact_geo_entity_str}"
    logger = set_up_detailedfilelogger(loggername=trial_name,  # same name as module, so logger is shared
                                       filename=trial_logfilename + '.log',
                                       level=log_level,
                                       also_logtoconsole=True,
                                       add_filehandler_if_already_exists=True,
                                       add_consolehandler_if_already_exists=False)
    logger_study = set_up_detailedfilelogger(loggername=studyshortname,  # same name as module, so logger is shared
                                             filename=f"step1_s{studyid}_{compact_geo_entity_str}.log",
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
    logger.debug(f"control file being used is: {control_file}")

    # If using s3, saved model instance is pulled from bucket.
    if use_s3_ws:
        pull_model_instance_from_s3(log_level=log_level, model_instance_name=saved_model_name, s3ops=s3ops)

    # Progress report is updated.
    progress_dict = read_control(control_file_name=control_dict['experiment']['uuid'])
    progress_dict['run_timestamps']['step4_trial_start'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    trial_uuid = control_dict['trial']['uuid']

    # *****************************
    # Make Model Modification(s)
    # *****************************
    my_model = load_model_pickle(savepath=saved_model_file, dryrun=dryrun, logprefix=logprefix)
    # Modification string is converted into a proper dictionary.
    modification_dict_withtrials = json.loads(model_modification_string)
    if not modification_dict_withtrials:
        modvar = None
        varvalue = None
    else:
        modvar, varvalue = make_model_modification(modification_dict_withtrials, dryrun, my_model, logger)

    # *********************
    # Solve
    # *********************
    notreal_notimestamp_outputdfpath = os.path.join(get_output_dir(s3=False), f"solution_{trial_name}_<timestamp>.csv")

    if notdry(dryrun, logger, f"--Dryrun-- Would run trial and save outputdf at: {notreal_notimestamp_outputdfpath}"):
        # ---- Directory preparation ----
        s3_destination_dir = s3_base_path + compact_geo_entity_str + '/' + objective_and_constraint_str + '/'
        # Solutions directory is created if it doesn't exist.
        solutions_dir = os.path.join(get_output_dir(s3=False), solutions_folder_name)
        logger.debug(f"solutions_dir = {solutions_dir}")
        os.makedirs(solutions_dir, exist_ok=True)

        solvehandler = SolveHandler()

        solver_log_file = os.path.join(get_logging_dir(s3=False), trial_logfilename + '_ipopt.log')
        solver_iters_file = os.path.join(get_logging_dir(s3=False), trial_uuid + '_ipopt.iters')

        # The problem is solved.
        solution_dict = solvehandler.basic_solve(mdl=my_model, translate_to_cast_format=translate_to_cast_format,
                                                 solverlogfile=solver_log_file, solveritersfile=solver_iters_file)
        solution_dict['solution_df']['feasible'] = solution_dict['feasible']
        logger.info(f"Trial '{trial_name}' is DONE "
                    f"(@{solution_dict['timestamp']})! "
                    f"<Solution feasible? --> {solution_dict['feasible']}> ")
        logger_feasibility.info(f"<feasible: {solution_dict['feasible']}> for {saved_model_name}_{trial_name}")
        logger_study.info(f"trial {trial_name} is DONE")

        # The progress file is updated, then moved to output directory in s3.
        progress_dict['run_timestamps']['step4_trial_done'] = datetime.datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        iters, ipopt_time, n_vars, n_ineq_constraints, n_eq_constraints = IpoptParser().quickparse(solver_log_file)
        progress_dict['solve_characteristics'] = {'n_iterations': iters,
                                                  'solve_time (s)': ipopt_time,
                                                  'n_variables': n_vars,
                                                  'n_ineq_constraints': n_ineq_constraints,
                                                  'n_eq_constraints': n_eq_constraints}
        progress_file_name = write_progress_file(progress_dict, control_name=trial_uuid)

        if save_to_s3:
            # Progress file is moved to s3.
            return_code = s3ops.move_to_s3(local_path=os.path.join(get_control_dir(s3=False), progress_file_name + '.yaml'),
                                           destination_path=f"{s3_destination_dir + progress_file_name + '.yaml'}")
            logger.info(f"Move the progress file to s3 - exited with code <{return_code}>")
            # Solver output is moved to s3 also.
            return_code = s3ops.move_to_s3(local_path=solver_log_file,
                                           destination_path=f"{s3_destination_dir + trial_uuid + '_ipopt.log'}")
            logger.info(f"Move the solver log file to s3 - exited with code <{return_code}>")
            return_code = s3ops.move_to_s3(local_path=solver_iters_file,
                                           destination_path=f"{s3_destination_dir + trial_uuid + '_ipopt.iters'}")
            logger.info(f"Move the solver iters file to s3 - exited with code <{return_code}>")

        # Optimization objective value is added to the solution table.
        ii = 0
        for objective_component in my_model.component_objects(pyo.Objective):
            if ii < 1:
                # check whether Objective is an "indexed" component or not
                if objective_component._index == {None}:
                    solution_dict['solution_df']['solution_objective'] = pyo.value(objective_component)
                else:
                    for cidxpart in objective_component:
                        if objective_component[cidxpart].active:
                            solution_dict['solution_df']['solution_objective'] = pyo.value(objective_component[cidxpart])

                ii += 1
            else:
                logger.info('more than one objective found, only using one')
                break

        # Value of modified variable is added to the solution table.
        solution_dict['solution_df'][modvar] = varvalue
        # solution_dict['solution_df']['solution_mainconstraint_Percent_Reduction'] = pyo.value(mdlhandler.model.Percent_Reduction['N'].body)

        # *********************
        # Solution is saved.
        # *********************

        # Optimization solution table is written to file (uses comma-delimiter and .csv extention)
        solution_shortname = f"{trial_name}_{solution_dict['timestamp']}.csv"
        solution_fullname = f"{saved_model_name}_{trial_name}_{solution_dict['timestamp']}.csv"

        outputdfpath_bayotaformat = os.path.join(solutions_dir, solution_fullname)
        solution_dict['solution_df'].to_csv(outputdfpath_bayotaformat)
        logger.info(f"<Solution written to: {outputdfpath_bayotaformat}>")
        logger_study.info(f"<trial {trial_name} - solution written to: {outputdfpath_bayotaformat}>")

        if save_to_s3 and move_solution_to_s3:
            return_code = s3ops.move_to_s3(local_path=outputdfpath_bayotaformat,
                                           destination_path=f"{s3_destination_dir + solution_shortname}")
            logger.info(f"Move-the-solution-to-s3 script exited with code <{return_code}>")
            logger_study.info(f"trial {trial_name} - move-the-solution-to-s3 script exited with code <{return_code}>")

        # CAST-formatted solution table is written to file (uses tab-delimiter and .txt extention).
        if translate_to_cast_format:
            solution_shortname_castformat = f"castformat_{trial_name}_{solution_dict['timestamp']}.txt"
            solution_fullname_castformat = f"castformat_{saved_model_name}_{trial_name}_{solution_dict['timestamp']}.txt"

            outputdfpath_castformat = os.path.join(solutions_dir, solution_fullname_castformat)
            csv_string = solution_dict['cast_formatted_df'].to_csv(None, sep='\t', header=True,
                                                                   index=False, line_terminator='\r\n')
            open(outputdfpath_castformat, 'w').write(csv_string[:-2])  # -2 to remove blank line at end of file
            logger.info(f"<CAST-formatted solution written to: {outputdfpath_castformat}>")

            if save_to_s3 and move_CASTformatted_solution_to_s3:
                return_code = s3ops.move_to_s3(local_path=outputdfpath_castformat,
                                               destination_path=f"{s3_destination_dir + solution_shortname_castformat}")
                logger.info(f"Move-the-solution-to-s3 script exited with code <{return_code}>")

    return 0  # a clean, no-issue, exit


def make_model_modification(dictwithtrials, dryrun, model, logger):
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
            setattr(model, modvar, varvalue)
    else:
        if notdry(dryrun, logger, '--Dryrun-- Would make model modification; '
                                  'setting %s to %s (at index %s)' %
                                  (modvar, varvalue, varindexer)):
            model.component(modvar)[varindexer] = varvalue

    return modvar, varvalue


def parse_cli_arguments():
    """ Input arguments are parsed. """
    parser = ArgumentParser(description="Solve an optimization trial")

    parser.add_argument("control_filename", metavar='Control Filename', type=str,
                        help="name for this trial's control file")

    parser.add_argument("-d", "--dryrun", action='store_true',
                        help="run through the script without triggering any other scripts")

    parser.add_argument("--use_s3_ws", dest="use_s3_ws", action='store_true',
                        help="Pull workspace files from s3 bucket to local workspace at start of running this step")

    parser.add_argument("--save_to_s3", dest="save_to_s3", action='store_true',
                        help="Move model instance and progress files from local workspace to s3 buckets")

    parser.add_argument("--log_level", nargs=None, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="change logging level to {debug, info, warning, error, critical}")

    return parser.parse_args()


if __name__ == '__main__':
    opts = parse_cli_arguments()

    # The main function is called.
    sys.exit(main(opts.control_filename,
                  dryrun=opts.dryrun,
                  use_s3_ws=opts.use_s3_ws,
                  save_to_s3=opts.save_to_s3,
                  log_level=opts.log_level))
