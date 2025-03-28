import os, time
from simnibs import opt_struct
import numpy as np
import simnibs

def opt(path, list):
    print(path)
    rele = input('选择电极半径(mm):')
    mix = input('选择非ROI区域的最大阈值(V/m):')
    max = input('选择ROI区域的最小阈值(V/m):')
    A = input('选择单对电极电流大小(mA):')
    roi = input('选择目标ROI(格式：x,y,z 或 x y z):')
    rroi = input('选择ROI半径(mm):')
    coords_mni = np.array([float(coord) for coord in roi.replace(',', ' ').split()])
    print('开始处理')
    start_time = time.time()
    for i in list:
        start_timee = time.time()
        print('转换个体空间坐标')
        coords_subject = simnibs.mni2subject_coords([coords_mni], f'{path}/pre/{i}/m2m_{i}')
        formatted_coords = [round(coord, 1) for coord in coords_subject[0]]
        print(i,'roi is',formatted_coords)
        ''' Initialize structure '''
        opt = opt_struct.TesFlexOptimization()
        opt.subpath = f'{path}/pre/{i}/m2m_{i}'
        opt.output_folder = f"{path}/pre/{i}/m2m_{i}/TI_opt"

        ''' Set up goal function '''
        opt.goal = "focality"
        opt.threshold = [float(mix), float(max)]
        opt.e_postproc = "max_TI"
        ''' Define first electrode pair '''
        electrode_layout = opt.add_electrode_layout("ElectrodeArrayPair")
        electrode_layout.radius = [float(rele)]
        electrode_layout.current = [float(A), -float(A)]

        ''' Define second electrode pair '''
        electrode_layout = opt.add_electrode_layout("ElectrodeArrayPair")
        electrode_layout.radius = [float(rele)]
        electrode_layout.current = [float(A), -float(A)]

        ''' Define ROI '''
        roi = opt.add_roi()
        roi.method = "surface"
        roi.surface_type = "central"
        roi.roi_sphere_center_space = "subject"
        roi.roi_sphere_center = formatted_coords
        roi.roi_sphere_radius = float(rroi)
        # uncomment for visual control of ROI:
        # roi.subpath = opt.subpath
        # roi.write_visualization('','roi.msh')

        ''' Define non-ROI '''
        non_roi = opt.add_roi()
        non_roi.method = "surface"
        non_roi.surface_type = "central"
        non_roi.roi_sphere_center_space = "subject"
        non_roi.roi_sphere_center = formatted_coords
        non_roi.roi_sphere_radius = float(rroi) + 5
        non_roi.roi_sphere_operator = ["difference"]  # take difference between GM surface and the sphere region
        # uncomment for visual control of non-ROI:
        # non_roi.subpath = opt.subpath
        # non_roi.write_visualization('','non-roi.msh')

        ''' Run optimization '''
        opt.run()

        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_timee
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        print(f"处理{i}结束，共花费时间：{hours}小时{minutes}分{seconds}秒")

    end_time = time.time()
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    print(f"运行结束，共花费时间：{hours}小时{minutes}分{seconds}秒")