''' Example of a SimNIBS tDCS leadfield in Python
    Run with:

    simnibs_python leadfield.py

    Copyright (C) 2019 Guilherme B Saturnino

    place script in the main folder of the example dataset
'''
from simnibs import sim_struct, run_simnibs

'''s = sim_struct.SESSION()
tdcs_list = s.add_tdcslist()'''

tdcs_lf = sim_struct.TDCSLEADFIELD()
# subject folder
tdcs_lf.subpath = 'D:\\moni\\m2m_Sub032'
# output directory
tdcs_lf.pathfem = 'D:\\moni\\m2m_Sub032\\leadfield'

# Whether to calculate the electric field ‘E’ or current density ‘J’.
# tdcs_lf.field = 'E'

# egg_cap.csv field location
# tdcs_lf.eeg_cap = 'D:\\app\\simNIBS\\simnibs4_examples\\m2m_ernie\\eeg_positions\\EEG10-20_extended_SPM12'

# tdcs_lf.electrode = tdcs_list.add_electrode()

tdcs_lf.electrode.dimensions = [15, 15]
tdcs_lf.electrode.shape = 'rect'
tdcs_lf.electrode.thickness = [5]

# Uncoment to use the pardiso solver
# tdcs_lf.solver_options = 'pardiso'
# This solver is faster than the default. However, it requires much more
# memory (~12 GB)


run_simnibs(tdcs_lf)