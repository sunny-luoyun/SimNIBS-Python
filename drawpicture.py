import h5py
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.patches import Circle  # 导入 Circle 用于绘制圆形

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


def calculate_interference_field(leadfield_data, indices, current=0.01):
    """
    计算两个电极对产生的包络调制电场
    :param leadfield_data: 电场数据
    :param indices: 电极索引，前两个为一组，后两个为一组
    :param current: 输入电流大小（单位：A），默认为 1A
    """
    # 获取两组电极的电场数据
    field1 = leadfield_data[indices[0], :, :] * current
    field2 = -leadfield_data[indices[1], :, :] * current
    field3 = leadfield_data[indices[2], :, :] * current
    field4 = -leadfield_data[indices[3], :, :] * current

    # 计算每组电极的电场叠加
    combined_field1 = field1 + field2
    combined_field2 = field3 + field4

    # 计算包络调制电场
    E1 = np.linalg.norm(combined_field1, axis=1)
    E2 = np.linalg.norm(combined_field2, axis=1)

    phase_diff = np.arccos(np.clip(np.sum(combined_field1 * combined_field2, axis=1) / (E1 * E2), -1, 1))

    E_AM = np.zeros_like(E1)
    for i in range(len(E1)):
        if E1[i] > E2[i] and phase_diff[i] < np.pi / 2:
            E_AM[i] = 2 * E2[i]
        else:
            E_AM[i] = 2 * E2[i] * np.abs(np.sin(phase_diff[i] / 2))

    return E_AM


def visualize_2d_field_together(node_coords, field_magnitude, point, thickness=10):
    """
    可视化特定点所在的 x 平面、y 平面和 z 平面的二维电场分布，并将它们放在一个窗口中
    :param node_coords: 节点坐标
    :param field_magnitude: 电场幅度
    :param point: 特定点的坐标 (x, y, z)
    :param thickness: 平面的厚度
    """
    x, y, z = point

    # 创建一个包含三个子图的图形，启用 constrained_layout
    fig, axs = plt.subplots(1, 3, figsize=(20, 6), constrained_layout=True)

    # 提取 x 平面上的节点（范围为 x ± thickness/2）
    x_plane_indices = np.where((node_coords[:, 0] >= x - thickness / 2) & (node_coords[:, 0] <= x + thickness / 2))[0]
    if len(x_plane_indices) > 0:
        x_plane_coords = node_coords[x_plane_indices, 1:]  # 提取 y 和 z 坐标
        x_plane_field = field_magnitude[x_plane_indices]

        # 绘制 x 平面的电场分布
        sc = axs[0].scatter(x_plane_coords[:, 0], x_plane_coords[:, 1], c=x_plane_field, cmap='viridis', s=50)
        axs[0].set_xlabel('Y')
        axs[0].set_ylabel('Z')
        axs[0].set_title(f'Electric Field Distribution on X Plane (X = {x} ± {thickness/2})')

        # 在平面内绘制红色圆圈标记 point
        circle = Circle((y, z), thickness / 2, color='red', fill=False, linewidth=2)
        axs[0].add_patch(circle)

        # 设置等比例
        axs[0].set_aspect('equal')
    else:
        print(f"No nodes found on X plane (X = {x} ± {thickness/2})")

    # 提取 y 平面上的节点（范围为 y ± thickness/2）
    y_plane_indices = np.where((node_coords[:, 1] >= y - thickness / 2) & (node_coords[:, 1] <= y + thickness / 2))[0]
    if len(y_plane_indices) > 0:
        y_plane_coords = np.column_stack((node_coords[y_plane_indices, 0], node_coords[y_plane_indices, 2]))  # 提取 x 和 z 坐标
        y_plane_field = field_magnitude[y_plane_indices]

        # 绘制 y 平面的电场分布
        sc = axs[1].scatter(y_plane_coords[:, 0], y_plane_coords[:, 1], c=y_plane_field, cmap='viridis', s=50)
        axs[1].set_xlabel('X')
        axs[1].set_ylabel('Z')
        axs[1].set_title(f'Electric Field Distribution on Y Plane (Y = {y} ± {thickness/2})')

        # 在平面内绘制红色圆圈标记 point
        circle = Circle((x, z), thickness / 2, color='red', fill=False, linewidth=2)
        axs[1].add_patch(circle)

        # 设置等比例
        axs[1].set_aspect('equal')
    else:
        print(f"No nodes found on Y plane (Y = {y} ± {thickness/2})")

    # 提取 z 平面上的节点（范围为 z ± thickness/2）
    z_plane_indices = np.where((node_coords[:, 2] >= z - thickness / 2) & (node_coords[:, 2] <= z + thickness / 2))[0]
    if len(z_plane_indices) > 0:
        z_plane_coords = node_coords[z_plane_indices, :2]  # 提取 x 和 y 坐标
        z_plane_field = field_magnitude[z_plane_indices]

        # 绘制 z 平面的电场分布
        sc = axs[2].scatter(z_plane_coords[:, 0], z_plane_coords[:, 1], c=z_plane_field, cmap='viridis', s=50)
        axs[2].set_xlabel('X')
        axs[2].set_ylabel('Y')
        axs[2].set_title(f'Electric Field Distribution on Z Plane (Z = {z} ± {thickness/2})')

        # 在平面内绘制红色圆圈标记 point
        circle = Circle((x, y), thickness / 2, color='red', fill=False, linewidth=2)
        axs[2].add_patch(circle)

        # 设置等比例
        axs[2].set_aspect('equal')
    else:
        print(f"No nodes found on Z plane (Z = {z} ± {thickness/2})")

    # 添加颜色条
    cbar = fig.colorbar(sc, ax=axs, orientation='vertical', fraction=0.02, pad=0.04)
    cbar.set_label('Electric Field V/m')

    plt.show()

def calculate_electric_field(e1, e2, e3, e4, path, point, l, thickness=10):
    """
    计算指定电极的包络调制电场并可视化特定点所在的平面
    :param e1, e2, e3, e4: 四个电极名称
    :param path: HDF5 文件所在路径
    :param point: 特定点的坐标 (x, y, z)
    :param thickness: 平面的厚度
    """
    # 提取路径中的主体名称（例如 m2m_Sub001 中的 Sub001）
    subject_name = os.path.basename(path).split('_')[-1]

    # 构造 HDF5 文件路径
    hdf5_file = os.path.join(path, l, f'{subject_name}_leadfield_EEG10-10_UI_Jurak_2007.hdf5')

    # 加载数据
    leadfield_data, node_coords, electrode_names, electrode_pos = load_leadfield_data(hdf5_file)

    # 获取电极索引
    indices = get_electrode_indices(electrode_names, [e1, e2, e3, e4])

    # 计算包络调制电场
    E_AM = calculate_interference_field(leadfield_data, indices)

    # 可视化特定点所在的平面
    visualize_2d_field_together(node_coords, E_AM, point, thickness)


# 示例调用
if __name__ == "__main__":
    e1, e2, e3, e4 = 'F4', 'F6', 'F8', 'Fz'
    path = '/Users/langqin/Desktop/m2m_Sub012'
    point = (13.8, 1.3, 11.9)
    thickness = 10  # 设置厚度
    l = 'leadfield'
    calculate_electric_field(e1, e2, e3, e4, path, point,l, thickness)