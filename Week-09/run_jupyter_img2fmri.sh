#!/bin/bash -i
#SBATCH --partition normal
#SBATCH -c 1
#SBATCH --time 4:00:00
#SBATCH --mem-per-cpu 20G
#SBATCH --job-name tunnel
#SBATCH --output logs/jupyter-log-%J.txt

# setup the environment
source /farmshare/home/classes/psych/236/software/mambaforge/bin/activate
conda activate img2fmri
server=$(hostname)
module load afni
module load fsl # Not the traditional set up, since you need to append (rather than prepend) the python paths

## get tunneling info
XDG_RUNTIME_DIR=""
ipnport=$(shuf -i8000-9999 -n1)
ipnip=$(hostname -i)
## print tunneling instructions to jupyter-log-{jobid}.txt
echo -e "
    Copy/Paste this in your local terminal to ssh tunnel with remote
    -----------------------------------------------------------------
    ssh -N -L $ipnport:$ipnip:$ipnport $USER@${server}.stanford.edu
    -----------------------------------------------------------------

    Then open a browser on your local machine to the following address
    ------------------------------------------------------------------
    localhost:$ipnport  (prefix w/ https:// if using password)
    ------------------------------------------------------------------
    "

## start an ipcluster instance and launch jupyter
jupyter-notebook --no-browser --port=$ipnport --ip=$ipnip
