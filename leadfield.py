from simnibs import sim_struct, run_simnibs

tdcs_lf = sim_struct.TDCSLEADFIELD()
# subject folder
tdcs_lf.subpath = '/Users/langqin/Desktop/m2m_Sub001'
# output directory
tdcs_lf.pathfem = 'leadfield'


# Uncoment to use the pardiso solver
#tdcs_lf.solver_options = 'pardiso'
# This solver is faster than the default. However, it requires much more
# memory (~12 GB)


run_simnibs(tdcs_lf)