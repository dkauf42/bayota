#!/bin/csh

if( $(#argv} > 0 ) then
    set STUDY = $argv[1]
else
    echo 'Usage: csh run_bayota.csh <study_name>'; echo
    echo 'Enter name of the Study: '
    set STUDY = $<
    set INTERACTIVE = 1
endif

echo ''
echo 'Locating SETTINGS Configuration File...'
if ( ! -e ../../config/cloudfish/settings_config.cfg ) then
    echo 'Error'; exit;
endif

source ../../config/cloudfish/settings_config.cfg

set TIME_STAMP       = `date +%Y%m%d-%H%M%S`
set MONTH_STAMP      = `date +%Y%m`


# Directories to store Output and Logs
set OUT_DIR = ${OUTPUT_DIR_STEM}_${MONTH_STAMP}
mkdir -p $OUT_DIR

if ( ! ($?PRIORITY) ) set PRIORITY = 5000

echo 'Study: **' $STUDY '** in ' $PROJECT_HOME
echo 'Job Priority = ' $PRIORITY
echo ''
echo 'Continue? [Y/N]'
set response = $<

if ( $response == 'Y' || $response == 'y' ) then
    sbatch --nice=$PRIORITY --job-name=$STUDY ../bayota_efficiency.py

    set iRETURN = $?

    if ( $iRETURN == 1 ) then
        echo 'SLURM Unable to Queue'
    else
        echo ''
        echo 'Running'
        echo ''
    endif
endif