from copy import deepcopy
import os
import numpy as np
from simnibs import sim_struct, run_simnibs, mesh_io, ElementTags
from simnibs.utils import TI_utils as TI
import look_roi_efield
"""
     set up and run simulations for the two electrode pairs
"""
def sim(e1,e2,e3,e4,path,r,roi):
    folder_name = os.path.basename(path)
    sub = folder_name[4:]

    # specify general parameters
    S = sim_struct.SESSION()
    S.subpath = path  # m2m-folder of the subject
    S.pathfem = os.path.join(path, "TI")  # Directory for the simulation

    # specify first electrode pair
    tdcs = S.add_tdcslist()
    tdcs.currents = [0.01, -0.01]  # Current flow though each channel (A)

    electrode = tdcs.add_electrode()
    electrode.channelnr = 1
    electrode.centre = e1
    electrode.shape = 'ellipse'
    electrode.dimensions = [10, 10]  # diameter in [mm]
    electrode.thickness = 2  # 2 mm thickness

    electrode = tdcs.add_electrode()
    electrode.channelnr = 2
    electrode.centre = e2
    electrode.shape = 'ellipse'
    electrode.dimensions = [10, 10]
    electrode.thickness = 2

    # specify second electrode pair
    tdcs = S.add_tdcslist(deepcopy(tdcs))
    tdcs.electrode[0].centre = e3
    tdcs.electrode[1].centre = e4

    S.open_in_gmsh = False

    run_simnibs(S)

    """
        generate the TI field from the simulation results
    """
    m1 = mesh_io.read_msh(os.path.join(S.pathfem, f'{sub}_TDCS_1_scalar.msh'))
    m2 = mesh_io.read_msh(os.path.join(S.pathfem, f'{sub}_TDCS_2_scalar.msh'))

    # remove all tetrahedra and triangles belonging to the electrodes so that
    # the two meshes have same number of elements
    tags_keep = np.hstack((np.arange(ElementTags.TH_START, ElementTags.SALINE_START - 1),
                           np.arange(ElementTags.TH_SURFACE_START, ElementTags.SALINE_TH_SURFACE_START - 1)))
    m1 = m1.crop_mesh(tags=tags_keep)
    m2 = m2.crop_mesh(tags=tags_keep)

    # calculate the maximal amplitude of the TI envelope
    ef1 = m1.field['E']
    ef2 = m2.field['E']
    TImax = TI.get_maxTI(ef1.value, ef2.value)

    # make a new mesh for visualization of the field strengths
    # and the amplitude of the TI envelope
    mout = deepcopy(m1)
    mout.elmdata = []
    mout.add_element_field(ef1.norm(), 'magnE - pair 1')
    mout.add_element_field(ef2.norm(), 'magnE - pair 2')
    mout.add_element_field(TImax, 'TImax')
    mesh_io.write_msh(mout, os.path.join(S.pathfem, 'TI.msh'))
    v = mout.view(
        visible_tags=[1002, 1006],
        visible_fields='TImax',
    )
    v.write_opt(os.path.join(S.pathfem, 'TI.msh'))
    mesh_io.open_in_gmsh = False

    """read_results"""

    return look_roi_efield.main(path,r,roi)


if __name__ == "__main__":
    # checkpoint_file = "/Users/langqin/Desktop/m2m_Sub001/checkpoint.pkl"  # 检查点文件路径
    sim(
        e1='TP8',
        e2='Fz',
        e3='F8',
        e4='TP7',
        path='/Users/langqin/software/simnibs4_examples/m2m_MNI152',
        r=10,
        roi=[11.7, -2.4, -6.1]

    )