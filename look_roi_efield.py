import simnibs
import numpy as np
roi = input('选择目标ROI(格式：x,y,z 或 x y z):')

coords_mni = np.array([float(coord) for coord in roi.replace(',', ' ').split()])
coords_subject = simnibs.mni2subject_coords([coords_mni], f'/Users/langqin/software/simnibs4_examples/m2m_ernie')
formatted_coords = [round(coord, 1) for coord in coords_subject[0]]
print('roi is',formatted_coords)