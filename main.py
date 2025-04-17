import os,genetic_algorithm

# 路径输入
path = input("输入路径")
folder_name = os.path.basename(path)

if folder_name.startswith("m2m_"):
    # 提取 "m2m_" 之后的部分
    xxx = folder_name[4:]
    print("处理的被试为:", xxx)
else:
    print("路径不符合预期格式")
roi = input('输入ROI的MNI坐标')
roi_list = [float(coord) for coord in roi.replace(',', ' ').split()]
print('输入ROI为',roi_list)
r = input('输入半径')
r = float(r)
e = input('输入电场大小')
e = float(e)
# 函数运行
genetic_algorithm.genetic_algorithm(
        population_size=20,
        max_generations=200,
        crossover_rate=0.6,
        mutation_rate=0.2,
        fitness_threshold=e,
        elite_size=5,
        path = path,
        r = r,
        roi = roi_list
    )