# Utility file for MMN course

# Import broad libraries
import numpy as np 
import os
import glob
import scipy.io
from scipy import stats
from copy import deepcopy
from matplotlib import pyplot as plt
import pandas as pd 
import time
import inspect
from IPython.display import Image
from mpi4py import MPI


# Nibabel functions
import nibabel as nib
from nibabel import processing

# sklearn functions
from sklearn import preprocessing
from sklearn import metrics
from sklearn import manifold
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import PredefinedSplit


# Nilearn functions
import nilearn
from nilearn import datasets
from nilearn import surface
from nilearn import plotting
from nilearn.masking import compute_epi_mask
from nilearn.maskers import NiftiMasker, NiftiLabelsMasker

# Brainiak functions
import brainiak
from brainiak import image, io
from brainiak.isc import isc, isfc, permutation_isc
from brainiak.utils import fmrisim as sim
from brainiak.searchlight.searchlight import Searchlight
from brainiak.funcalign.srm import SRM

# Data path: Where the data for the tutorials is stored.
# Change this path only if you have saved the data to a different folder.
data_path = '/farmshare/home/classes/psych/236/data/'

# Where are the atlases you are using in this course stored?
atlas_path = '/farmshare/home/classes/psych/236/atlases/'

# for Sherlock dataset
sherlock_dir = data_path + 'Sherlock/'

# for Pieman2 dataset
pieman2_dir =  os.path.join(data_path, 'Pieman2')

# for Raider dataset
raider_data_dir = os.path.join(data_path, 'raider')


