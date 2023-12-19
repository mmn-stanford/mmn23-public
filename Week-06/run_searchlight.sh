#!/bin/bash
# Run a searchlight on a participant, using a specific kernel
#
#SBATCH --output=./logs/searchlight-%j.out
#SBATCH --job-name searchlight
#SBATCH -t 90        # time limit: how many minutes 
#SBATCH --mem=12G    # memory limit
#SBATCH -N 1         # Specify that you only want 1 Node 
#SBATCH -n 3         # how many tasks to use (which corresponds to cores for MPI)

# Set up the environment. 
source ./setup_environment.sh

# Receive the inputs to the searchlight script
ppt_number=$1 # The first input is the participant number, ranging from 1 to 17
kernel=$2 # The second input is the kernel you want to use, either 'calc_svm' or 'calc_rsa'

# Run the python script using MPI
mpirun python ./searchlight.py $ppt_number $kernel