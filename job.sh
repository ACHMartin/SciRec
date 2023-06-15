#!/bin/bash
#
#SBATCH -N 1
#SBATCH -n 16
#SBATCH --mem=48G
#SBATCH --partition=defaultq
#SBATCH --mail-type=all          # send email when job begins, ends and fails
#SBATCH --mail-user=daria.andrievskaia@noveltis.fr
#SBATCH --array=1-2

# Activate the virtual environment
source $HOME/.bashrc
conda activate seastar

$SLURM_ARRAY_TASK_ID


# Change to the directory containing the Python script
cd /NOVELTIS/andrievskaia/SeaSTAR/20230418_SciReC_simu

python united_script.py
