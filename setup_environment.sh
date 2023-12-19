#!/bin/bash -i

# Specify the server name you are going to use. This might be the address you use for your SSH key to log in to the cluster. The default is to use the host name that may be appropriate
server=$(hostname)

# Specify the code necessary to setup your environment to run BrainIAK on a Jupyter notebook. This could involve activating a conda environment (like below) or importing modules.
source /farmshare/home/classes/psych/236/software/mambaforge/bin/activate # First activate mamba so that you can get the conda environment
CONDA_ENV=brainiak

# Activate the conda environment
conda activate $CONDA_ENV

# Check if the conda command succeeded
if [[ $? -ne 0 ]]; then
    echo "Conda not initialized properly, check your conda environment"
    exit -1
fi
