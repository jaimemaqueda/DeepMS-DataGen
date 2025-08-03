import numpy as np

ALL_OPERATIONS = ['RS', 'Mill', 'Drill', 'Slant', 'EOS', 'FP']
RS_IDX = ALL_OPERATIONS.index('RS') # Raw Stock
MILL_IDX = ALL_OPERATIONS.index('Mill')
DRILL_IDX = ALL_OPERATIONS.index('Drill')
SLANT_IDX = ALL_OPERATIONS.index('Slant')
EOS_IDX = ALL_OPERATIONS.index('EOS') # End of Sequence
FP_IDX = ALL_OPERATIONS.index('FP') # Final Part

MAX_N_MILL = 4
MAX_N_DRILL = 5
MAX_N_SLANT = 1
MAX_TOTAL_LEN = MAX_N_DRILL + MAX_N_MILL + MAX_N_SLANT + 3 # maximum process planning sequence length (5 DRILL + 4 MILL + 1 SLANT + 1 FP + 1 RS + 1 EOS)

VOL_DIM = 128 # delta volume dimension for 3D voxelization
EOS_VOL = np.zeros((VOL_DIM, VOL_DIM, VOL_DIM), dtype=bool) # End of Sequence volume
