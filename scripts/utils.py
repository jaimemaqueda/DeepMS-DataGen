import os
import numpy as np
from .macro import *

def get_next_filenames(base_h5_dir='data/seq_h5', base_stl_dir='data/seq_stl', max_files_per_folder=3000):
 # Ensure base directories exist
    if not os.path.exists(base_h5_dir):
        os.makedirs(base_h5_dir)
    if not os.path.exists(base_stl_dir):
        os.makedirs(base_stl_dir)
    
    # Find the highest numbered folder in the H5 directory
    h5_folders = [f for f in os.listdir(base_h5_dir) if f.isdigit()]
    if not h5_folders:
        next_folder = '0000'
        next_h5_file = '00000000.h5'
    else:
        latest_h5_folder = max(h5_folders)
        h5_folder_path = os.path.join(base_h5_dir, latest_h5_folder)
        
        # Find the highest numbered file in the latest H5 folder
        h5_files = [f for f in os.listdir(h5_folder_path) if f.endswith('.h5') and f[:-3].isdigit()]
        if not h5_files:
            # No files in the latest folder
            next_h5_file = '00000000.h5'
            next_folder = latest_h5_folder
        elif len(h5_files) >= max_files_per_folder:
            # Folder is full, increment folder number and reset file number
            next_h5_file = '00000000.h5'
            next_folder = str(int(latest_h5_folder) + 1).zfill(4)
        else:
            # Increment file number within the current folder
            latest_h5_file = max(h5_files)
            next_file_number = str(int(latest_h5_file[:-3]) + 1).zfill(8)
            next_h5_file = next_file_number + '.h5'
            next_folder = latest_h5_folder

    # Create necessary folder structure if it does not exist
    next_h5_folder_path = os.path.join(base_h5_dir, next_folder)
    if not os.path.exists(next_h5_folder_path):
        os.makedirs(next_h5_folder_path)
    
    next_h5_file_path = os.path.join(next_h5_folder_path, next_h5_file)

    # Create the corresponding STL filename
    next_stl_folder_path = os.path.join(base_stl_dir, next_folder)
    if not os.path.exists(next_stl_folder_path):
        os.makedirs(next_stl_folder_path)
    
    next_stl_file_path = os.path.join(next_stl_folder_path, next_h5_file[:-3] + '_00.stl')

    return next_h5_file_path, next_stl_file_path

def get_next_stl_filename(stl_file_path):
    base, ext = os.path.splitext(stl_file_path)
    if not base[-2:].isdigit():
        raise ValueError("The provided path does not end with a valid _XX suffix.")

    base_number = int(base[-2:])
    next_number = str(base_number + 1).zfill(2)
    next_stl_file_path = f"{base[:-2]}{next_number}{ext}"
    return next_stl_file_path

def select_feature_combinations():
    # Define the feature combinations and their corresponding cases
    combinations = [
        (10, [MILL_IDX, SLANT_IDX, DRILL_IDX], "No Intersection"),
        (3, [MILL_IDX, SLANT_IDX], "No Intersection"),
        (3, [MILL_IDX, DRILL_IDX], "No Intersection"),
        (3, [SLANT_IDX, DRILL_IDX], "No Intersection"),
        (1, [MILL_IDX], "No Intersection"),
        (1, [SLANT_IDX], "No Intersection"),
        (1, [DRILL_IDX], "No Intersection"),
        (10, [SLANT_IDX, MILL_IDX, DRILL_IDX], "Intersection Mill-Slant"),
        (3, [SLANT_IDX, MILL_IDX], "Intersection Mill-Slant"),
        (10, [MILL_IDX, DRILL_IDX, SLANT_IDX], "Intersection Drill-Slant"),
        (3, [DRILL_IDX, SLANT_IDX], "Intersection Drill-Slant"),
        (10, [DRILL_IDX, MILL_IDX, SLANT_IDX], "Intersection Mill-Drill"),
        (3, [DRILL_IDX, MILL_IDX], "Intersection Mill-Drill"),
        (10, [DRILL_IDX, SLANT_IDX, MILL_IDX], "Intersection Mill-Drill Mill-Slant Drill-Slant"),
        (10, [SLANT_IDX, DRILL_IDX, MILL_IDX], "Intersection Mill-Drill Mill-Slant"),
    ]
    weights = [c[0] for c in combinations]
    idx = np.random.choice(len(combinations), p=weights/np.sum(weights))
    combination = combinations[idx][1]
    case = combinations[idx][2]
    return combination, case

class SurfaceMap:
    def __init__(self, length, width, dtype=bool):
        self.length = length
        self.width = width
        self.grid = np.zeros((length, width), dtype=dtype)
    
    def is_free(self, start_i, end_i, start_j, end_j):
        return not np.any(self.grid[start_i:end_i, start_j:end_j])
    
    def is_not_free(self, start_i, end_i, start_j, end_j):
        return np.any(self.grid[start_i:end_i, start_j:end_j])