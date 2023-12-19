# Setting up img2fmri

An important goal of this course is to give you a foundation upon which you can incorporate new methods into research. This week, we are going to be using methods on the **bleeding edge** of fMRI that require some setup, which this README will guide you through. Indeed, although setting up software that people use for their analyses can be cumbersome and slow, you should also take away that it isn't *that* hard to do this. The code base we will be using today is particularly didactic and easy to use, but this is by no means an exception. 

You will need to follow the steps below **precisely** or else you may not set up your environment correctly and will need to start again (let us know if this happens, since we will probably have to delete the conda environment). You will need to do this in the command line on Farmshare, rather than in the notebook, since these commands require selecting options. All of the code you enter assumes you are in the folder for this week's assignment. 

You only need to set this code up once. When it is working, you will just need to do Step 7 to reopen your notebooks.

If you feel like the steps below don't meet your needs (e.g., you want a docker) you can find the original installation instructions [here](https://github.com/dpmlab/img2fmri/tree/main). However, that is discouraged for most members of the class.   

Setting this up will take some time to install. While it is loading, you should read the notebook on github. You can read through and formulate your answers to the first few questions (which don't need code).  
 
## Step 1: Get on a node
**Estimated run time: 3 minutes**

Rather than running your analyses on the login node, where the work you will be doing will drain the resources from others, you should run your analyses on a node just for you. Specifically, you are going to request a node for 60 minutes. After 60 minutes, this will crash, but hopefully this will be long enough for your needs.

>`srun --pty -p normal -t 60:00 bash`

This will take a few minutes to find you resources to run the job, but when it does you will have a normal terminal to execute commands in.

If you need to cancel the job at any point -- or you have finished -- just type `exit` into the command window.

## Step 2: Create a new conda environment
**Estimated run time: 3 minutes**

We are now going to create a clean conda environment in which we can install the packages we need. You can think of conda environments like an account you log into on the computer that you can install software on, without affecting other accounts in the computer. You have been using conda environments,throughout this course, specifically one called `brainiak` that you have loaded in when you run `launch_jupyter.sh`. Now, you are going to make your own, that you will use later to load in to launch a jupyter notebook. The first line will load in the software for making conda environments (mamba) and then you will make a conda environment called `img2fmri`

>`source /farmshare/home/classes/psych/236/software/mambaforge/bin/activate`  
>`conda create --name img2fmri python=3.9`

After a few minutes of running, this will ask you whether you want to install certain packages, type `y` and press return. When it finishes, the command line will be returned to you (i.e., you will be able to type and submit new commands). The last few lines of the output will include instructions on how to activate the environment, like we will do in the next step.

**Self-study:** It is best practice to always put your conda environments in a folder that isn't your home directory. This is because your home directory is usually space-constrained and conda environments can get large. To change where conda environments are stored, you must edit your `~/.condarc` file (more info <a href=https://conda.io/projects/conda/en/latest/user-guide/configuration/use-condarc.html> here</a>). We are not doing that here though, because we don't have another storage place other than this for farmshare.


## Step 3: Activate the conda environment
**Estimated run time: 1 minute**

Now that you have the conda environment, you have to activate it so that we can install software in there 

>`conda activate img2fmri`

## Step 4: Install the necessary packages using pip
**Estimated run time: 15 minutes**

So we have a nearly empty conda environment, let's fill it with all of the software you will need. Primarily, we need to install the software for `img2fmri`, which includes tools for computer vision and machine learning. Additionally, we need some basic software for opening jupyter notebooks and other functions (e.g., visualization).

>`pip install img2fmri notebook pandas matplotlib nilearn`

This line will take a long time to run. It may freeze at a point and look like nothing is happening. However, it is likely still processing. That said, if nothing changes in 20 minutes, let us know and we will come try help.

**Self-study:** For those in the know, you might wonder why we are using `pip install` instead of `conda install`. `img2fmri` is set up for pip rather than conda, and so even though we can install things like jupyter with conda instead, it is more likely to cause unresolvable conflicts when you have a mixture of pip and conda installs. In general, pip is best if your code all involves python, whereas use conda if you are using multiple languages. 

## Step 5: Clone repository
**Estimated run time: 1 minute**

Now that the software is installed, we want to get some of the functions we will use in today's notebook. You can get that by cloning this git repo into your folder.

>`git clone https://github.com/dpmlab/img2fmri.git`

## Step 6: Remove git information from the cloned repo
**Estimated run time: 1 minute**

You now have a public repo inside the class repo but nesting repos within repos can cause problems. We are going to delete the functionality for the newly downloaded repo so that it can no longer interact with git (specifically, we will scrub it's information about where it came from). That way you won't be able to accidentally push your class assignment to the `img2fmri` public git repo!

>`rm -rf img2fmri/.git/`

## Step 7: Launch new jupyter notebook
**Estimated run time: 2 minutes**

You have now finished setting up, and you don't need the job started in step 1. You should cancel it for cleanliness (but keep this window open) by typing `exit` into the command window.

Now you can start the jupyter-notebook since you have the proper environment. Specifically, you should run the following command:

>`sbatch ./run_jupyter_img2fmri.sh`

This is a variant of the script you have run for every class to start a jupyter notebook, but now using the conda environment you made and other softwares we need (FSL and AFNI). 

Once you have submitted this job, you can open up the log file that is created with the following command:

>`cat logs/*$JOBID*` where `$JOBID` will be the 7 digit number that is printed out when you submitted the jupyter job.

You will notice that the jupyter notebook is a little different looking -- it is a newer version -- but you should have most of the same functionality.

**Critically: now that you have set up the environment, you only have to redo step 7 when you log back on to Farmshare to work on this assignment.**  

**DO NOT REPEAT ANY OF THE OTHER STEPS**
