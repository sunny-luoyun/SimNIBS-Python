from copy import deepcopy
import os
import numpy as np
from simnibs import sim_struct, run_simnibs, mesh_io, ElementTags
from simnibs.utils import TI_utils as TI
import look_roi_efield
import string
import random

def generate_random_path(base_path, length=5):
    # 生成一个随机路径名
    letters = string.ascii_lowercase
    random_string = ''.join(random.choice(letters) for _ in range(length))
    return os.path.join(base_path, random_string)

def sim(e1, e2, e3, e4, path, r, roi, ma, idx):
    folder_name = os.path.basename(path)
    sub = folder_name[4:]

    # 生成随机的输出路径
    random_output_path = generate_random_path(path)
    os.makedirs(random_output_path, exist_ok=True)  # 确保路径存在

    S = sim_struct.SESSION()
    S.subpath = path  # m2m 文件路径
    S.pathfem = random_output_path  # 使用随机生成的路径作为输出目录

    tdcs = S.add_tdcslist()
    tdcs.currents = [ma, -ma]  # 电流强度mA

    # 设置各向异性类型为 'vn'
    tdcs.anisotropy_type = 'vn'  # 使用体积归一化的各向异性导电性

    # 设置各向异性参数
    tdcs.aniso_maxratio = 10  # 最大各向异性比率
    tdcs.aniso_maxcond = 2  # 最大导电性值

    electrode = tdcs.add_electrode()
    electrode.channelnr = 1
    electrode.centre = e1
    electrode.shape = 'ellipse'
    electrode.dimensions = [10, 10]  # 电极半径mm
    electrode.thickness = 2  # 电极厚度mm

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

    # 计算TI包络场强

    m1 = mesh_io.read_msh(os.path.join(S.pathfem, f'{sub}_TDCS_1_vn.msh'))
    m2 = mesh_io.read_msh(os.path.join(S.pathfem, f'{sub}_TDCS_2_vn.msh'))

    tags_keep = np.hstack((np.arange(ElementTags.TH_START, ElementTags.SALINE_START - 1),
                           np.arange(ElementTags.TH_SURFACE_START, ElementTags.SALINE_TH_SURFACE_START - 1)))
    m1 = m1.crop_mesh(tags=tags_keep)
    m2 = m2.crop_mesh(tags=tags_keep)

    ef1 = m1.field['E']
    ef2 = m2.field['E']
    TImax = TI.get_maxTI(ef1.value, ef2.value)

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

    # 查看模拟结果

    field_strength = look_roi_efield.main(path, r, roi, random_output_path)
    print(idx, field_strength)
    return (idx, field_strength)

if __name__ == "__main__":
    sim(e1='CP1',
        e2='F2',
        e3='F6',
        e4='PO7',
        path='/Users/langqin/data/m2m_Sub001',
        r=10,
        roi=[13.8, 1.3, 11.9],
        ma = 0.01,
        idx=None
        )
