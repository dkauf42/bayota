#!/bin/bash

MY_HOME=/home/dkaufman
PROJECT_HOME=${MY_HOME}/bayota
PYTHON_ENTRY_SCRIPT_DIR=${PROJECT_HOME}/bin

#BINPATH=`dirname $0`

echo

# start script with --daemon as an argument to restart itself
# detached from the current shell.
case "$1" in
    -d|--daemon)
        $0 < /dev/null &> /dev/null & disown
        exit 0
        ;;
    *)
        ;;
esac

"$PYTHON_ENTRY_SCRIPT_DIR/bayota_efficiency.py" $@