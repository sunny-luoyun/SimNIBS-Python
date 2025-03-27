import os, time
"""
Example to run TESoptimize for Temporal Interference (TI) to optimize the 
focality in the ROI vs non-ROI

Copyright (c) 2024 SimNIBS developers. Licensed under the GPL v3.
"""
from simnibs import opt_struct


def opt(path, list):
    start_time = time.time()
    for i in list:
        start_timee = time.time()

        ''' Initialize structure '''
        opt = opt_struct.TesFlexOptimization()
        opt.subpath = f'{path}/pre/m2m_{i}'
        opt.output_folder = f"{path}/pre/m2m_{i}/ti_focality"

        ''' Set up goal function '''
        opt.goal = "focality"
        opt.threshold = [0.1, 0.2]
        opt.e_postproc = "max_TI"
        ''' Define first electrode pair '''
        electrode_layout = opt.add_electrode_layout("ElectrodeArrayPair")
        electrode_layout.radius = [10]
        electrode_layout.current = [0.002, -0.002]

        ''' Define second electrode pair '''
        electrode_layout = opt.add_electrode_layout("ElectrodeArrayPair")
        electrode_layout.radius = [10]
        electrode_layout.current = [0.002, -0.002]

        ''' Define ROI '''
        roi = opt.add_roi()
        roi.method = "surface"
        roi.surface_type = "central"
        roi.roi_sphere_center_space = "subject"
        roi.roi_sphere_center = [-41.0, -13.0, 66.0]
        roi.roi_sphere_radius = 20
        # uncomment for visual control of ROI:
        # roi.subpath = opt.subpath
        # roi.write_visualization('','roi.msh')

        ''' Define non-ROI '''
        non_roi = opt.add_roi()
        non_roi.method = "surface"
        non_roi.surface_type = "central"
        non_roi.roi_sphere_center_space = "subject"
        non_roi.roi_sphere_center = [-41.0, -13.0, 66.0]
        non_roi.roi_sphere_radius = 25
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