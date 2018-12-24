#!/bin/bash

# The PROJECT_HOME and SLURM_OUTPUT path variables are read_spec from local configuration.
source ${HOME}/.config/${USER}/bayota_bash_config.con
echo 'PROJECT_HOME is loaded: ' ${PROJECT_HOME}
echo 'SLURM_OUTPUT is loaded: ' ${SLURM_OUTPUT}

# A name for this Study is requested from the user.
if [ $# -gt 0 ]; then
    STUDY=$1
else
    echo 'Usage: ./conduct_study.bash <study_name>'
    echo ''
    echo 'Enter name of the Study: '
    read STUDY
    INTERACTIVE=1
fi


# The Study specification file is defined and its variables are read_spec.
STUDY_SPEC_FILE=${PROJECT_HOME}/bin/studies/${STUDY}.ini
echo ''
echo ${STUDY_SPEC_FILE}
echo 'Locating Study Specification File...'
if [ ! -f ${STUDY_SPEC_FILE} ]; then
    echo 'Error'
    exit 1
fi

# Study configuration attributes are printed in the console.
OBJECTIVE=$(awk -F " = " '/^objective/ {gsub(/[ \t]/, "", $2); print $2}' ${STUDY_SPEC_FILE})
SCALE=$(awk -F " = " '/^scale/ {gsub(/[ \t]/, "", $2); print $2}' ${STUDY_SPEC_FILE})
ENTITIES=$(awk -F " = " '/^entities/ {gsub(/[ \t]/, "", $2); print $2}' ${STUDY_SPEC_FILE})
echo 'objective is loaded: ' ${OBJECTIVE}
echo 'scale is loaded: ' ${SCALE}
echo 'entities are loaded: ' ${ENTITIES}


# Date/time stamps are defined.
#timestamp() { date +"%Y%m%d-%H%M%S" }
#monthstamp() { date +"%Y%m" }
TIME_STAMP=$(date +"%Y%m%d-%H%M%S")
MONTH_STAMP=$(date +"%Y%m")


## Directories to store output/logs are created.
#OUT_DIR=${OUTPUT_DIR_STEM}_${MONTH_STAMP}
#mkdir -p $OUT_DIR


# Compute parameters are given for this batch job.
if [ -z ${PRIORITY} ]; then
    PRIORITY=5000
fi
NUMNODES=1


# The slurm batch command is set up.

# SBATCH -n 1      # tasks requested
# SBATCH -c 4      # cores requested
# SBATCH --mem=10  # memory in Mb
# SBATCH --output=logs/multiprocess_%j.out
# SBATCH -o outfile  # send stdout to outfile
# SBATCH -e errfile  # send stderr to errfile

CMD="sbatch "
CMD+="--job-name=${STUDY} "
CMD+="--nice=${PRIORITY} "
CMD+="--nodes=${NUMNODES} "      # nodes requested
CMD+="--output=${SLURM_OUTPUT} "
CMD+="--time=01:00:00 "          # time requested in hour:minute:second
CMD+="${PROJECT_HOME}/bin/cli/conductor_cli.py -c ${STUDY_SPEC_FILE}"

# The user is asked for confirmation to start the job.
echo ''
echo '*** *** *** *** ***'
echo 'Study: **' ${STUDY} '** in ' ${PROJECT_HOME}
echo '-- Job Priority = ' ${PRIORITY}
echo '-- Number of nodes = ' ${NUMNODES}
echo ''
echo 'Command is: '
echo ${CMD}
echo '*** *** *** *** ***'
echo ''
echo 'Continue? [Y/N]'
read response


# The batch job is sent to the Slurm manager.
if [ ${response} = 'Y' ] || [ ${response} = 'y' ]; then
    eval ${CMD}

    iRETURN=$?

    if [ ${iRETURN} -eq 1 ]; then
        echo 'SLURM Unable to Queue'
    else
        echo ''
        echo 'Running'
        echo ''
        echo 'Slurm output will be written to: ' ${SLURM_OUTPUT}
    fi
fi
