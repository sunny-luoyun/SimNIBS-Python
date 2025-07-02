import os
import subprocess
import shutil

def convert_dicom_to_nifti(input_path, output_path,sub):
    """
    检查输入路径，如果是NIfTI文件则返回其路径，如果是包含DICOM文件的文件夹则将其转换为NIf格式TI。

    :param input_path: 输入文件或文件夹路径
    :param output_path: 输出路径
    :return: 转换后的NIfTI文件路径或输入的NIfTI文件路径
    """
    # 检查输入路径是否存在
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入路径 {input_path} 不存在。")

    # 检查输入路径是否为文件
    if os.path.isfile(input_path):
        # 检查文件扩展名是否为NIfTI格式
        if input_path.endswith(('.nii', '.nii.gz')):
            return input_path
        else:
            raise ValueError(f"输入文件 {input_path} 不是NIfTI格式。")
    # 检查输入路径是否为文件夹
    elif os.path.isdir(input_path):
        # 构造dcm2niix命令
        command = f"dcm2niix -o '{output_path}' -f '{sub}T1' -z y -s y '{input_path}'"
        # 执行命令
        try:
            subprocess.run(command, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"执行dcm2niix命令时出错：{e}")

        # 获取输出文件路径
        output_file = os.path.join(output_path, f"{sub}T1.nii.gz")
        if not os.path.exists(output_file):
            raise FileNotFoundError(f"转换后的NIfTI文件 {output_file} 未找到。")

        return output_file
    else:
        raise ValueError(f"输入路径 {input_path} 既不是文件也不是文件夹。")

def charm():
    input_path = input("请输入结构像NIFTI文件或DICOM文件夹路径")
    output_path = input('请输入文件输出路径')
    sub = input('请输入被试编号(如:Sub001)')
    path = convert_dicom_to_nifti(input_path,output_path,sub)
    print(path)
    cmd = f'charm {sub} {path} --forcerun'
    subprocess.run(cmd, shell=True, check=True)
    # 获取当前程序的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 构造m2m文件夹的绝对路径
    m2m_folder = os.path.join(current_dir, f'm2m_{sub}')

    # 检查文件夹是否存在
    if os.path.exists(m2m_folder):
        # 构造目标路径
        target_path = os.path.join(output_path, f'm2m_{sub}')
        # 移动文件夹
        shutil.move(m2m_folder, target_path)
        print(f'文件夹{m2m_folder}已移动到{target_path}')
    else:
        print(f'文件夹{m2m_folder}不存在，无法移动')

if __name__ == "__main__":
    charm()