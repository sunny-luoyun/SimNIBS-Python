''' Example of a SimNIBS tDCS optimization in Python
    Run with:

    simnibs_python tdcs_optimize.py

    Copyright (C) 2019 Guilherme B Saturnino
'''

import simnibs

# Initialize structure
opt = simnibs.opt_struct.TDCSoptimize()
# Select the leadfield file
opt.leadfield_hdf = 'D:\\moni\\m2m_Sub032\\leadfield\\Sub032_leadfield_EEG10-10_UI_Jurak_2007.hdf5'
# Select a name for the optimization
opt.name = 'D:\\moni\\m2m_Sub032\\optimization\\test1'

# Select a maximum total current (in A)
opt.max_total_current = 5e-3
# Select a maximum current at each electrodes (in A)
opt.max_individual_current = 5e-3
# Select a maximum number of active electrodes (optional)
opt.max_active_electrodes = 4

# Define optimization target
target = opt.add_target()

# subject space
# target.positions = [-37, -21, 58]
# MNI space
target.positions = simnibs.mni2subject_coords([28, 4, -4], 'D:\\moni\\m2m_Sub032')

# Intensity of the electric field (in V/m)
target.intensity = 0.8

# Set the intensity to a large value (e.g, 100)
# target.intensity = 100

opt.open_in_gmsh = False

simnibs.run_simnibs(opt)
