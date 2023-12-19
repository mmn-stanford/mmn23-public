#!/bin/bash -i
#SBATCH --partition normal
#SBATCH -c 1
#SBATCH --time 4:00:00
#SBATCH --mem-per-cpu 20G
#SBATCH --job-name tunnel
#SBATCH --output logs/jupyter-log-%J.txt

# setup the environment
source setup_environment.sh

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
