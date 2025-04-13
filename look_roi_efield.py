import os
import numpy as np
import simnibs
def main(path,rr,roii):
    # 读取刺激结果，file放入刺激上一步骤刺激所生成的文件夹路径
    newpath = os.path.join(path, "TI")
    mshpath = os.path.join(newpath, "TI.msh")
    head_mesh = simnibs.read_msh(
        os.path.join('file', mshpath)
    )

    # 划分出灰质
    gray_matter = head_mesh.crop_mesh(simnibs.ElementTags.GM)

    # 设定要观察的ROI位置
    ernie_coords = simnibs.mni2subject_coords(roii, path)
    # 以roi为中心半径10mm的小球
    r = rr

    # 获取平均场强
    elm_centers = gray_matter.elements_baricenters()[:]
    roi = np.linalg.norm(elm_centers - ernie_coords, axis=1) < r
    elm_vols = gray_matter.elements_volumes_and_areas()[:]

    # 放置roi小球
    gray_matter.add_element_field(roi, 'roi')
    gray_matter.view(visible_fields='roi').show()

    # 得到小球内电场
    field_name = 'TImax'
    field = gray_matter.field[field_name][:]

    # 输出结果
    mean_magnE = np.average(field[roi], weights=elm_vols[roi])

    process = os.popen(
        f'rm -r {newpath}')
    output = process.read()
    print(output)
    process.close()

    return mean_magnE