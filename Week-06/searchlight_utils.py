import sys
sys.path.insert(0, '..')
from utils import *
from mpi4py import MPI

def prepare_sherlock_4D(ppt):
    """
    Load a Sherlock participant's data as a 4d volume.
    These functions are pulled from week 2, with a tweak for making a 4d volume
    
    Parameters:
        ppt: the participant ID e.g., 'sub-01'
    
    Returns:
        func_vol: A 4d volume of the participant's sherlock data for both segments
        mask: A 3d volume of the voxels that contained brain data. This is the intersect of all masks from all participants
        affine: The affine matrix describing the orientation of the brain data
    """ 

    # What is the file name? We are getting participant 1
    file = sherlock_dir + '/derivatives/movie_files/%s.nii.gz' % (ppt)

    # Create the nifti object that serves as a header
    func_nii = nib.load(file)

    # Load the data volume
    print('Loading fMRI data for %s, this will take a minute' % ppt)
    func_vol = func_nii.get_fdata()
    print('Finished loading data')

    # Load the mask. THis is shared across participants
    mask = nib.load(sherlock_dir + '/derivatives/searchlights/whole_brain_mask.nii.gz').get_fdata()
    
    # Store the affine matrix of the data
    affine = func_nii.affine
    
    # Return the functional data and the mask
    return func_vol, mask, affine



def generate_classifier_labels():
    """
    Select the time points and get the labels in order to do classification of whether someone was speaking during Sherlock
     
    Returns
        observation_TRs_shifted: A dictionary containing the time points from the first or second segment that were chosen. These time points are sufficiently separated in time to allow for independent observations
        labels: A dictionary of the condition labels for all of the observations that were selected, separated for the first and second half
    """

    # 1. PRESET VARIABLES
    condition_key = 'is_speaking' # What is the condition you are testing
    TR_separation = 8 # What is the minimum number of TRs that separate two observations
    TR_buffer = 3 # How many TRs on each side of the current TR must be the same condition for it to be used
    lag_shift = 6 # How many seconds is the shift you will apply to the labels to account for hemodynamic lag?
    TR_duration = 1.5 # How many seconds is each TR
    TR_lag_shift = int(lag_shift / TR_duration) # Convert the lag shift into TRs
    first_segment_duration = 946 # How long was the first movie segment

    binarized_label = [] # Preset a list
    TR_condition = {} 
    observation_TRs_raw = {}
    observation_TRs_shifted = {}
    labels = {}
    observation_TRs_raw[condition_key] = {'first_segment': [], 'second_segment': []} # preset
    observation_TRs_shifted = {}
    labels = {} # What are the labels for the observations stored


    # 2. LOAD IN THE DATA FRAME
    pd.set_option('display.max_rows', 1000)
    df = pd.read_csv('%s/derivatives/event_file.csv' % sherlock_dir)


    # 3. CREATE A NEW VARIABLE FOR WHETHER SOMEONE IS SPEAKING OR NOT
    TR_condition[condition_key] = np.ones((int(np.nanmax(df[' End Time (s) ']) / TR_duration, ))) * np.nan # Make an array of nans that is the length of the movie
    for speaker in df['Name_Speaking']:

        # When no one is speaking, the label is 'nan', nans are weird python values where nan != nan
        if speaker != speaker:
            binarized_label += [0]
        else:
            binarized_label += [1]


    # 4. SPECIFY THE TIMES AT WHICH EACH EPOCH STARTS AND ENDS
    for segment_counter, condition in enumerate(binarized_label):

        start_time = df['Start Time (s) '][segment_counter]
        end_time = df[' End Time (s) '][segment_counter]
        num_TR = np.round((end_time - start_time) / TR_duration)

        start_idx = int(np.round(start_time / TR_duration))
        end_idx = int(np.round(end_time / TR_duration))

        # Store the condition labels
        TR_condition[condition_key][start_idx:end_idx] = condition


    # 5. FIND TIME POINTS FROM EACH CONDITION THAT ARE SUFFICIENTLY SEPARATED IN TIME
    for TR_counter in range(len(TR_condition[condition_key])):

        # Make sure there is space around the events to be considered at all (we include the lag_shift variable, which we will return to in a minute)
        if (TR_counter >= TR_buffer) and (TR_counter < len(TR_condition[condition_key]) - TR_buffer - 1):

            # What are the indexes for the buffer
            start_idx = TR_counter - TR_buffer
            end_idx = TR_counter + TR_buffer

            # Decide what segment the participant is in
            if (start_idx <= first_segment_duration) and (end_idx <= first_segment_duration): 
                # If the start and end index are BEFORE the end of the first segment, it is first segment
                segment_name = 'first_segment'

            elif (start_idx >= first_segment_duration) and (end_idx >= first_segment_duration): 
                # If the start and end index are AFTER the end of the first segment, it is second segment
                segment_name = 'second_segment'

            else:
                # If the buffer straddles between the first and second half, ignore it
                continue

            # CRITERIA 1: Check that all of the TRs are the same inside the buffer
            if len(np.unique(TR_condition[condition_key][start_idx:end_idx])) == 1:

                # CRITERIA 2: Now check that the last observation recorded wasn't closer than the minimum separation
                if np.all((TR_counter - TR_separation) >= np.asarray(observation_TRs_raw[condition_key][segment_name])):

                    # Since it has met both criteria, add it to the list
                    observation_TRs_raw[condition_key][segment_name] += [TR_counter]


    # 6. TIMESHIFT AND STORE THE LABELS
    for segment_name in observation_TRs_raw[condition_key].keys():

        # Add the shift to the raw data
        observation_TRs_shifted[segment_name] = np.asarray(observation_TRs_raw[condition_key][segment_name]) + TR_lag_shift
        labels[segment_name] = np.asarray(TR_condition[condition_key])[np.asarray(observation_TRs_raw[condition_key][segment_name])]
    
    # Return the key outputs
    return observation_TRs_shifted, labels


def subsample_balance(data, labels):
    """
    This function makes sure that there are equal numbers of labels for the two conditions.
    To do this it subsamples the number of labels for the class that has more
    
    Parameters:
        data: Observation by feature numpy array
        labels: Binarized labels as a 1d numpy array
    
    Returns:
        data: Balanced observation by feature array
        labels: Balanced binarized labels
    
    """
    
    # Binarize the labels for simplicity
    labels = labels > 0
    
    # Find which label is most common
    counts = np.bincount(labels)
    most_common = np.argmax(counts)

    # How many trials of the less common label are there?
    min_count = np.min(counts)

    # Get the indexes corresponding to the most common label
    most_common_idxs = np.where(labels == most_common)[0]
    less_common_idxs = np.where(labels != most_common)[0] # Get this so you have it for later

    # Now shuffle the most common indexes and take the top N, where N is the same as the less common number
    np.random.shuffle(most_common_idxs) 
    most_common_idxs = most_common_idxs[:min_count]

    # Now concatenate the usable indexes
    usable_idxs = np.concatenate((most_common_idxs, less_common_idxs))

    # Now crop the data accordingly
    data = data[usable_idxs, :]
    labels = labels[usable_idxs, ]
    
    # Return the newly cropped data
    return data, labels

# Set up a RSA kernel function
def calc_rsa(data, sl_mask, myrad, bcvar):
    
    """
    Create an RSA from brain activity and compare it to the model activity
    
    Parameters
        data: a list of 4D arrays containing data of voxels within a searchlight
        sl_mask: a binary mask centered on voxels at the centers of the searchlights.
        myrad: (integer) the radius of the searchlight
        bcvar: the data broadcast to each searchlight, used in the kernel calculation (here, the model representation)
        
    Returns:
        r_val: correlation between the model and human representation
    """
        
    # Check if there are enough voxels
    if np.sum(sl_mask) < (np.size(sl_mask) / 2):
            
        # If there are fewer than half of the masked voxels then return a zero
        return None
        
    model_vec = bcvar # This is the data broadcasted to all your searchlights.
    
    # Convert the data into a voxel by time array and remove the voxels outside of the mask. 
    data_mat = data[0][sl_mask == 1]
    
    # Compute a timepoint by timepoint similarity matrix of the data
    TSM = np.corrcoef(data_mat.T)
    
    # Convert the matrix into a vector, removing the buffer near the diagonal. This is hard coded as 10 based on the model
    human_vec = np.triu(TSM, k=10)
    human_vec = human_vec[human_vec != 0]

    # Compute the correlation
    r_val = np.corrcoef(human_vec, model_vec)[0, 1]
    
    return r_val

# Set up a RSA kernel function
def calc_svm(data, sl_mask, myrad, bcvar):
    
    """
    Create an RSA from brain activity and compare it to the model activity
    
    Parameters
        data: a list of 4D arrays containing data of voxels within a searchlight. The first array is the first segment, the second is the second segment
        sl_mask: a binary mask centered on voxels at the centers of the searchlights.
        myrad: (integer) the radius of the searchlight
        bcvar: the data broadcast to each searchlight, used in the kernel calculation (here, the list of labels)
        
    Returns:
        accuracy: average classification accuracy after cross-validation
    """
    
    # Check if there are enough voxels 
    if np.sum(sl_mask) < (np.size(sl_mask) / 2):

        # If there are fewer than half of the masked voxels then return a zero
        return None
    
    # Decide whether the first or second segment is the training data
    accuracy = []
    for train_counter in [0, 1]:

        # This is the data broadcasted to all your searchlights.
        train_labels = np.copy(bcvar[train_counter])
        test_labels  = np.copy(bcvar[1 - train_counter])
        
        # Convert the data into a voxel by time array and remove the voxels outside of the mask. 
        train_data = data[train_counter][sl_mask == 1].T
        test_data = data[1 - train_counter][sl_mask == 1].T
        
        # Subsample the data to balance conditions
        train_data, train_labels = subsample_balance(train_data, train_labels)
        test_data, test_labels = subsample_balance(test_data, test_labels)

        # Create a linear SVC model with hyperparameter C set to 0.01.  
        model = SVC(kernel="linear", C=0.01)

        # Fit the model on the BOLD data and corresponding stimulus labels.
        model.fit(X=train_data, y=train_labels)

        # Score your model on the test data.
        accuracy += [model.score(X=test_data, y=test_labels)]
        
    return np.mean(accuracy)