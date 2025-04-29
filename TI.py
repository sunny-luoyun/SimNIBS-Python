import h5py
import numpy as np
import os


def load_leadfield_data(hdf5_file):
    """加载 HDF5 文件中的 leadfield 数据和电极信息"""
    with h5py.File(hdf5_file, 'r') as f:
        # 加载电场数据
        leadfield_data = f['mesh_leadfield/leadfields/tdcs_leadfield'][:]

        # 加载节点坐标
        node_coords = f['mesh_leadfield/nodes/node_coord'][:]

        # 获取电极名称和位置
        electrode_names = f['mesh_leadfield/leadfields/tdcs_leadfield'].attrs['electrode_names']
        electrode_pos = f['mesh_leadfield/leadfields/tdcs_leadfield'].attrs['electrode_pos']

        return leadfield_data, node_coords, electrode_names, electrode_pos


def get_electrode_indices(electrode_names, target_electrodes):
    """根据电极名称获取它们的索引"""
    indices = []
    for name in target_electrodes:
        if name in electrode_names:
            indices.append(np.where(electrode_names == name)[0][0])
        else:
            raise ValueError(f"Electrode '{name}' not found in the dataset.")
    return indices


def calculate_interference_field(leadfield_data, indices, current=0.005):
    """
    计算两个电极对产生的包络调制电场
    :param leadfield_data: 电场数据
    :param indices: 电极索引，前两个为一组，后两个为一组
    :param current: 输入电流大小（单位：A），默认为 1A
    """
    # 获取两组电极的电场数据
    field1 = leadfield_data[indices[0], :, :] * current
    field2 = leadfield_data[indices[1], :, :] * current
    field3 = leadfield_data[indices[2], :, :] * current
    field4 = leadfield_data[indices[3], :, :] * current

    # 计算每组电极的电场叠加
    combined_field1 = field1 + field2
    combined_field2 = field3 + field4

    # 计算包络调制电场
    # 根据文章中的公式 (2)
    E1 = np.linalg.norm(combined_field1, axis=1)
    E2 = np.linalg.norm(combined_field2, axis=1)

    # 计算相位差
    phase_diff = np.arccos(np.clip(np.sum(combined_field1 * combined_field2, axis=1) / (E1 * E2), -1, 1))

    # 计算包络调制电场的幅度
    E_AM = np.zeros_like(E1)
    for i in range(len(E1)):
        if E1[i] > E2[i] and phase_diff[i] < np.pi / 2:
            E_AM[i] = 2 * E2[i]
        else:
            E_AM[i] = 2 * E2[i] * np.abs(np.sin(phase_diff[i] / 2))

    return E_AM


def calculate_average_field_in_roi(node_coords, field_magnitude, roi_center, roi_radius):
    """
    计算球形区域内的平均电场大小
    :param node_coords: 节点坐标
    :param field_magnitude: 电场幅度
    :param roi_center: 球形区域的中心坐标 (x, y, z)
    :param roi_radius: 球形区域的半径
    :return: 球形区域内的平均电场大小
    """
    # 计算每个节点到球心的距离
    distances = np.linalg.norm(node_coords - roi_center, axis=1)

    # 找出位于球形区域内的节点索引
    roi_indices = np.where(distances <= roi_radius)[0]

    # 如果球形区域内没有节点，返回 None
    if len(roi_indices) == 0:
        return None

    # 计算球形区域内的平均电场大小
    average_field = np.mean(field_magnitude[roi_indices])
    return average_field


def calculate_electric_field(e1, e2, e3, e4, path, r, roi, idx):
    """
    计算指定电极和区域的平均电场大小
    :param e1, e2, e3, e4: 四个电极名称
    :param path: HDF5 文件所在路径
    :param r: 球形区域的半径
    :param roi: 球形区域的中心坐标 [x, y, z]
    :return: 球形区域内的平均电场大小
    """
    # 提取路径中的主体名称（例如 m2m_Sub001 中的 Sub001）
    subject_name = os.path.basename(path).split('_')[-1]

    # 构造 HDF5 文件路径
    hdf5_file = os.path.join(path, 'leadfield', f'{subject_name}_leadfield_EEG10-10_UI_Jurak_2007.hdf5')

    # 加载数据
    leadfield_data, node_coords, electrode_names, electrode_pos = load_leadfield_data(hdf5_file)

    # 获取电极索引
    indices = get_electrode_indices(electrode_names, [e1, e2, e3, e4])

    # 计算包络调制电场
    E_AM = calculate_interference_field(leadfield_data, indices)

    # 计算球形区域内的平均电场大小
    average_field = calculate_average_field_in_roi(node_coords, E_AM, np.array(roi), r)
    print(idx, average_field)

    return (idx, average_field)


# 示例调用
if __name__ == "__main__":
    e1, e2, e3, e4 = 'Fz', 'F8', 'TP7', 'TP8'
    path = '/Users/langqin/Desktop/m2m_Sub001'
    r = 10.0
    roi = [28.0, 4.0, -4.0]
    idx = None
    calculate_electric_field(e1, e2, e3, e4, path, r, roi, idx)
