# Run a whole brain searchlight on the Sherlock movie data
# This script takes in a participant ID and a kernel and then applies it to the whole brain.

# Import libraries
import sys
sys.path.insert(0, '..')

# Suppress the warnings for depreciation that clog this up
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning) 
warnings.simplefilter(action='ignore', category=FutureWarning)

from utils import *
from mpi4py import MPI
from brainiak.searchlight.searchlight import Searchlight # Get the specific name of the searchlight function for ease
from searchlight_utils import * # Get the searchlight utility functions


########### Specify the input arguments. This sets default values if none are provided

# Get the participant counter (ranging from 1 to 17)
if len(sys.argv) > 1:
    ppt_counter = int(sys.argv[1])
else:
    ppt_counter = 1

# What is the name of the kernel you want to run
if len(sys.argv) > 2:
    kernel_name = sys.argv[2]
else:
    kernel_name = 'calc_rsa'
    

########### Set up some parameters that will be used throughout

TR_duration = 1.5 # How many seconds is each TR
first_segment_duration = 946 # How long was the first movie segment
ppt_num = 17 # How many participants are there?

sl_rad = 1 # Specify the radius of the searchlight
max_blk_edge = 5 # Specify the size of the chunk to be handed to the MPI
pool_size = 1 # How many cores per chunk

ppt = 'sub-%02d' % ppt_counter # What is the name of the participant input
output_file = './searchlight_%s_%s.nii.gz' % (kernel_name, ppt) # Specify the name of the output file

# Pull out the MPI information
comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size

########### Set up the parameters only to broadcast to the first process, specifically the fMRI data
if rank == 0:
    
    print('Running %s with the %s kernel. Using %d processes. Starting at %s' % (ppt, kernel_name, size, time.ctime(time.time())))
    
    func_vol, mask, affine = prepare_sherlock_4D(ppt)
    
    # Preprocess the functional data according to the which type of kernel you are running
    if kernel_name == 'calc_rsa':
        func_vol_2nd = func_vol[:, :, :, first_segment_duration:]

        # Specify the data to give to the searchlight   
        data = [func_vol_2nd]
        
    elif kernel_name == 'calc_svm':
        
        # Run the script to get the classifier labels
        observation_TRs_shifted, labels = generate_classifier_labels()

        # Trim the data to only include the relevant observations
        func_vol_1st_observations = func_vol[:, :, :, observation_TRs_shifted['first_segment']]
        func_vol_2nd_observations = func_vol[:, :, :, observation_TRs_shifted['second_segment']]

        # Specify the data to give to the searchlight
        data = [func_vol_1st_observations, func_vol_2nd_observations] # Separate the data for the first and second segments
        
else:
    
    # If you aren't on the first rank then load in the mask from a different place
    mask = nib.load(sherlock_dir + '/derivatives/searchlights/whole_brain_mask.nii.gz').get_fdata()
    
    if kernel_name == 'calc_rsa':
        data = [None] # Specify as None
    else:
        data = [None, None] # Specify as a list of Nones
    

########### Set up the variables to broadcast to all processes

# If you are doing calc_rsa then do the following
if kernel_name == 'calc_rsa':
    
    # Load in the off-diagonal of the model
    bcvar =  np.load('alex_fc6_rsm.npy') # The model to do the comparison to brain data with
    
    kernel = calc_rsa # What is the function you are going to perform inside the kernel  
    
    
# Set up the data differently for SVM
elif kernel_name == 'calc_svm':
    
    # Run the script to get the classifier labels. This was done above, but needs to be done again for all ranks
    observation_TRs_shifted, labels = generate_classifier_labels()
    
    # Load in the labels, separate for each segment
    bcvar = [labels['first_segment'], labels['second_segment']]
    
    kernel = calc_svm
    
########### Set up the searchlight and run it   

# Create the searchlight object
sl = Searchlight(sl_rad=sl_rad,max_blk_edge=max_blk_edge)

# Distribute the information to the searchlights (preparing it to run)
sl.distribute(data, mask)

# Broadcast variables
sl.broadcast(bcvar)

# Run the searchlight analysis
print(f"Begin Searchlight in rank {rank}")
sl_result = sl.run_searchlight(kernel, pool_size=pool_size)
print(f"End Searchlight in rank {rank}")

########### Save the outputs of the searchlight

# Only save the data if this is the first rank.
if rank == 0: 
    
    sl_result = sl_result.astype('double')  # Convert the output into a precision format that can be used by other applications.
    sl_result[np.isnan(sl_result)] = 0  # Exchange nans with zero to ensure compatibility with other applications.

    # Save the result
    sl_nii = nib.Nifti1Image(sl_result, affine)
    nib.save(sl_nii, output_file)  # Save    
    
    print('Finished searchlight at %s' % time.ctime(time.time()))
