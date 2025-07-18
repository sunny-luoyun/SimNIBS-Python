"""
Example to run TESoptimize for Temporal Interference (TI) to optimize the
focality in the ROI vs non-ROI

Copyright (c) 2024 SimNIBS developers. Licensed under the GPL v3.
"""
import os.path

from simnibs import opt_struct
import time
def opt(path,roi_list,r,e, ma):
    st = time.time()
    ''' Initialize structure '''
    opt = opt_struct.TesFlexOptimization()
    opt.subpath = path                               # path of m2m folder containing the headmodel
    opt.output_folder = os.path.join(path,'tes_optimize_ti_focality')

    ''' Set up goal function '''
    opt.goal = "focality"                                   # optimize the focality of "max_TI" in the ROI ("max_TI" defined by e_postproc)
    opt.threshold = e                              # define threshold(s) of the electric field in V/m in the non-ROI and the ROI:
                                                            # if one threshold is defined, it is the goal that the e-field in the non-ROI is lower than this value and higher than this value in the ROI
                                                            # if two thresholds are defined, the first one is the threshold of the non-ROI and the second one is for the ROI
    opt.e_postproc = "max_TI"                               # postprocessing of e-fields
                                                            # "max_TI": maximal envelope of TI field magnitude
                                                            # "dir_TI_normal": envelope of normal component
                                                            # "dir_TI_tangential": envelope of tangential component
    ''' Define first electrode pair '''
    electrode_layout = opt.add_electrode_layout("ElectrodeArrayPair")   # Pair of TES electrode arrays (here: 1 electrode per array)
    electrode_layout.radius = [10]                                      # radii of electrodes
    electrode_layout.current = [ma, -ma]                          # electrode currents

    ''' Define second electrode pair '''
    electrode_layout = opt.add_electrode_layout("ElectrodeArrayPair")
    electrode_layout.radius = [10]
    electrode_layout.current = [ma, -ma]

    ''' Define ROI '''
    roi = opt.add_roi()

    # roi.method = "volume"
    roi.label = [1,2]

    roi.method = "surface"
    roi.surface_type = "central" # define ROI on central GM surfaces

    roi.roi_sphere_center_space = "subject"
    roi.roi_sphere_center = roi_list           # center of spherical ROI in subject space (in mm)
    roi.roi_sphere_radius = r                              # radius of spherical ROI (in mm)
    # uncomment for visual control of ROI:
    #roi.subpath = opt.subpath
    #roi.write_visualization('','roi.msh')

    ''' Define non-ROI '''
    # all of GM surface except a spherical region with 25 mm around roi center
    non_roi = opt.add_roi()

    # non_roi.method = "volume"
    non_roi.label = [1,2]

    non_roi.method = "surface"
    non_roi.surface_type = "central"
    non_roi.roi_sphere_center_space = "subject"
    non_roi.roi_sphere_center = roi_list
    non_roi.roi_sphere_radius = r + 10
    non_roi.roi_sphere_operator = ["difference"]                             # take difference between GM surface and the sphere region
    # uncomment for visual control of non-ROI:
    #non_roi.subpath = opt.subpath
    #non_roi.write_visualization('','non-roi.msh')
    opt.open_in_gmsh = False
    ''' Run optimization '''
    opt.run()


    et = time.time()
    elapsed_time = et - st
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    print(f"处理结束，共花费时间：{hours}小时{minutes}分{seconds}秒")