#!/bin/sh
#SBATCH --job-name=multiprocess
#SBATCH --nodes 1      # nodes requested
#SBATCH -n 1      # tasks requested
#SBATCH -c 4      # cores requested
#SBATCH --mem=10  # memory in Mb
#SBATCH --output=logs/multiprocess_%j.out
#SBATCH -o outfile  # send stdout to outfile
#SBATCH -e errfile  # send stderr to errfile
#SBATCH --time=00:01:00  # time requested in hour:minute:second

module load python
python run_without_scimode.py