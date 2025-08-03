import trimesh
import numpy as np
import h5py
import gc
import os
import glob
from scipy.ndimage import binary_fill_holes
from .macro import *
from .utils import get_next_filenames

class VoxelConverter:
    def __init__(self, filename, stl_filename, voxel_resolution=None):
        # Initialize with STL file and voxel grid parameters
        self.filename = filename
        self.stl_filename = stl_filename
        self.voxel_resolution = voxel_resolution if voxel_resolution is not None else np.array([128, 128, 128])
        self.voxels = None
        self.last_voxels = None

    def append_to_h5file(self, voxel_data, operation):
        with h5py.File(self.filename, 'a') as h5file:  # Open file in append mode
            if 'voxels' not in h5file:
                maxshape = (None,) + voxel_data.shape
                chunks = (1,) + voxel_data.shape  # Adjust chunk size as necessary
                h5file.create_dataset('voxels', data=[voxel_data], maxshape=maxshape, chunks=chunks, compression='gzip')
                h5file.create_dataset('operations', data=[operation], maxshape=(None,), chunks=(1,), compression='gzip')
            else:
                h5file['voxels'].resize((h5file['voxels'].shape[0] + 1), axis=0)
                h5file['voxels'][-1] = voxel_data
                h5file['operations'].resize((h5file['operations'].shape[0] + 1), axis=0)
                h5file['operations'][-1] = operation

    def convert_to_voxels(self, stl_file, operation=None):
        self.last_voxels = self.voxels.copy() if self.voxels is not None else None

        # Load the mesh from the STL file
        mesh = trimesh.load_mesh(stl_file)
        # Compute the voxel grid
        voxel_grid = mesh.voxelized(pitch=1, method='binvox').matrix
        voxel_grid = binary_fill_holes(voxel_grid)
        bbox = mesh.bounding_box.extents
        voxel_grid = voxel_grid[0:int(bbox[0]), 0:int(bbox[1]), 0:int(bbox[2])]
        resolution = self.voxel_resolution
        pad = [
            ((resolution[0] - voxel_grid.shape[0]) // 2, (resolution[0] - voxel_grid.shape[0] ) // 2 + (resolution[0] - voxel_grid.shape[0]) % 2),
            ((resolution[1] - voxel_grid.shape[1]) // 2, (resolution[1] - voxel_grid.shape[1] ) // 2 + (resolution[1] - voxel_grid.shape[1]) % 2),
            ((resolution[2] - voxel_grid.shape[2]) // 2, (resolution[2] - voxel_grid.shape[2] ) // 2 + (resolution[2] - voxel_grid.shape[2]) % 2)
        ]
        self.voxels = np.pad(voxel_grid, pad, mode='constant', constant_values=False)

        if operation is not None:
            # Store the voxel grid directly to the HDF5 file
            self.append_to_h5file(self.voxels, operation)

        # Release memory
        del mesh
        del voxel_grid
        del pad
        gc.collect()

    def compute_delta_volume(self, operation=None):
        if self.last_voxels is None or self.voxels is None:
            raise ValueError("Voxel grids must be initialized.")

        if self.last_voxels.shape != self.voxels.shape:
            raise ValueError("Voxel grids must have the same shape.")

        # Compute the difference between the two voxel grids (XOR operation)
        delta_voxels = np.logical_xor(self.last_voxels, self.voxels)

        if operation is not None:
            # Store the delta voxel grid directly to the HDF5 file
            self.append_to_h5file(delta_voxels, operation)

        # Release memory
        del delta_voxels
        gc.collect()

    def finalize(self, augmentation=False, base_h5_dir=None, base_stl_dir=None):
        repeat_sample = False
        # Store the last voxel grid (final part shape)
        if self.voxels is not None:
            self.append_to_h5file(self.voxels, FP_IDX)
            del self.voxels

        if augmentation:
            rotations = [
                lambda x: np.rot90(x, 1, axes=(0, 1)),  # Rotate 90 degrees around axes (0, 1)
                lambda x: np.rot90(x, 1, axes=(1, 2)),  # Rotate 90 degrees around axes (1, 2)
                lambda x: np.rot90(x, 1, axes=(2, 0)),  # Rotate 90 degrees around axes (2, 0)
                lambda x: np.rot90(x, 2, axes=(0, 1)),  # Rotate 180 degrees around axes (0, 1)
                lambda x: np.rot90(x, 2, axes=(1, 2))   # Rotate 180 degrees around axes (1, 2)
            ]

            with h5py.File(self.filename, 'r') as h5file:
                voxels_dataset = h5file['voxels']
                operations_dataset = h5file['operations']

                for idx, rotation in enumerate(rotations):
                    new_filename, _ = get_next_filenames(base_h5_dir, base_stl_dir, max_files_per_folder=3000)
                    self.filename = new_filename
                    
                    for i in range(voxels_dataset.shape[0]):
                        try:
                            voxel_rotated = rotation(voxels_dataset[i])
                            operation = operations_dataset[i]
                            if np.count_nonzero(voxel_rotated) <= 200:
                                raise ValueError("Voxel grid is empty after rotation.")
                            self.append_to_h5file(voxel_rotated, operation)
                            del voxel_rotated
                            gc.collect()

                        except Exception as e:
                            print(f"Error in the h5 file: {e}")
                            h5file.close()
                            base_number = int(self.filename[-11:-3])

                            # Remove matching STL files
                            stl_dirpath = os.path.dirname(self.stl_filename)
                            stl_basename = str(base_number - (idx + 1)).zfill(8)
                            pattern = f'{stl_basename}_??.stl'
                            stl_files = glob.glob(os.path.join(stl_dirpath, pattern))
                            for stl_file in stl_files:
                                os.remove(stl_file)

                            # Remove matching HDF5 files
                            for n in range(idx + 2):
                                try:
                                    filename_remove = self.filename[:-11] + str(base_number - n).zfill(8) + '.h5'
                                    os.remove(filename_remove)
                                except FileNotFoundError:
                                    continue
                            
                            print(f"Removed {stl_basename} files.")
                            repeat_sample = True
                            return repeat_sample
                     
        gc.collect()            
        return repeat_sample

               