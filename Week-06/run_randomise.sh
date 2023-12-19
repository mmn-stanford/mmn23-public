#!/bin/bash
# Run the FSL randomise function on the data

#SBATCH --output=./logs/randomise-%j.out
#SBATCH --job-name randomise
#SBATCH -t 20        # time limit: how many minutes 
#SBATCH --mem=12G    # memory limit
#SBATCH -n 1         # how many tasks to use

# Set up the environment.
module load fsl/6.0.7.4

# Receive the inputs to the searchlight script
input_file=$1 # The first input is the participant number, ranging from 1 to 17

# Pull out the kernel name. This assumes that the data has the form: PATH/searchlight_${kernel_name}_all.nii.gz
kernel_name=${input_file#*searchlight_}
kernel_name=${kernel_name%_all*}

# Decide the output data based on the kernel that was provided
output_file=./randomise_${kernel_name}

# Run Randomise. This does 1000 iterations
randomise -i ${input_file} -o ${output_file} -1 -n 1000 -x -T
