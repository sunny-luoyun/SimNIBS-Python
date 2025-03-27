import os
import numpy as np
import simnibs

pairs = [
    ("Fp1", "Fp2"), ("AF3", "AF4"), ("AF7", "AF8")
]
t = 1
n = len(pairs)
combinations = []

for i in range(n):
    for j in range(i + 1, n):
        combinations.append((pairs[i], pairs[j]))

for pair in combinations:
    a, b = pair[0]
    c, d = pair[1]


    # 查看roi单位电场强度

    # 读取刺激结果，file放入刺激上一步骤刺激所生成的文件夹路径
    head_mesh = simnibs.read_msh(
        os.path.join(f'/Users/sunny/Desktop/moni/m2m_Sub099/TI_Stimulation/{t}', f'/Users/sunny/Desktop/moni/m2m_Sub099/TI_Stimulation/{t}/TI.msh')
    )

    # 划分出灰质
    gray_matter = head_mesh.crop_mesh(simnibs.ElementTags.GM)

    # 设定要观察的ROI位置
    ernie_coords = simnibs.mni2subject_coords([22, -3, -4], '/Users/sunny/Desktop/moni/m2m_Sub099')
    # 以roi为中心半径10mm的小球
    r = 10.

    # 获取平均场强
    elm_centers = gray_matter.elements_baricenters()[:]
    roi = np.linalg.norm(elm_centers - ernie_coords, axis=1) < r
    elm_vols = gray_matter.elements_volumes_and_areas()[:]

    # 放置roi小球
    gray_matter.add_element_field(roi, 'roi')
    gray_matter.view(visible_fields='roi')

    # 得到小球内电场
    field_name = 'TImax'
    field = gray_matter.field[field_name][:]

    # 输出结果
    mean_magnE = np.average(field[roi], weights=elm_vols[roi])
    print(t, a, b, c, d, mean_magnE)

    t = t + 1
