import random
import os
import pickle
import concurrent.futures
import TI
import single_ti

# 对称电极对列表
symmetric_pairs = [
    ("Fp1", "Fp2"), ("AF3", "AF4"), ("AF7", "AF8"), ("F3", "F4"), ("F7", "F8"),
    ("FC3", "FC4"), ("FC5", "FC6"), ("FT7", "FT8"), ("C3", "C4"), ("C5", "C6"),
    ("CP3", "CP4"), ("CP5", "CP6"), ("TP7", "TP8"), ("P3", "P4"), ("P7", "P8"),
    ("PO3", "PO4"), ("PO7", "PO8"), ("O1", "O2"), ("F1", "F2"), ("F5", "F6"), ("FC1", "FC2"),
    ("C1", "C2"), ("CP1", "CP2"), ("P1", "P2")
]

# 获取所有可能的对称电极组合
def get_all_combinations(symmetric_pairs, num_pairs):
    from itertools import combinations
    all_combinations = list(combinations(symmetric_pairs, num_pairs))
    return [tuple(sorted([electrode for pair in combo for electrode in pair])) for combo in all_combinations]

# 计算适应度（多核版本）
def calculate_fitness(all_combinations, log_file, path, r, roi, fitness_cache, max_workers=None):
    fitness = [0] * len(all_combinations)  # 初始化适应度列表
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, individual in enumerate(all_combinations):
            if individual in fitness_cache:
                fitness[idx] = fitness_cache[individual]
                log_file.write(
                    f"Using cached fitness for combination {idx + 1}: {individual} -> Field Strength: {fitness_cache[individual]}\n")
                log_file.flush()
            else:
                # 提交任务时传递索引和电极组合
                futures.append(executor.submit(single_ti.sim, *individual, path, r, roi, idx))

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                idx = result[0]  # 获取返回的索引
                fitness_value = result[1]  # 获取返回的适应度值
                fitness[idx] = fitness_value
                fitness_cache[individual] = fitness_value
                log_file.write(f"Trying combination {idx + 1}: {all_combinations[idx]} -> Field Strength: {fitness_value}\n")
                log_file.flush()
            except Exception as e:
                log_file.write(f"Error occurred while calculating fitness for combination {idx + 1}: {all_combinations[idx]}\n")
                log_file.write(f"Error: {e}\n")
                log_file.flush()
                fitness[idx] = 0  # 如果出错，将适应度值设为 0
    return fitness

# 主程序
def exhaustive_search(num_pairs, path, r, roi, max_workers=50):
    log_file_path = os.path.join(path, "pair_results.txt")
    fitness_cache = {}  # 用于缓存适应度值

    with open(log_file_path, 'a') as log_file:
        log_file.write("Starting exhaustive search...\n")
        log_file.flush()

        # 获取所有可能的组合
        all_combinations = get_all_combinations(symmetric_pairs, num_pairs)
        log_file.write(f"Total combinations to evaluate: {len(all_combinations)}\n")
        log_file.flush()

        # 计算适应度
        fitness = calculate_fitness(all_combinations, log_file, path, r, roi, fitness_cache, max_workers)

        # 输出最优解
        best_index = fitness.index(max(fitness))
        best_individual = all_combinations[best_index]
        best_fitness = max(fitness)

        log_file.write("\nFinal result:\n")
        log_file.write(f"Optimal electrode combination: {best_individual}\n")
        log_file.write(f"Electric field strength: {best_fitness}\n")
        log_file.flush()

if __name__ == "__main__":
    exhaustive_search(
        num_pairs=2,  # 每个组合中对称电极对的数量
        path='/Users/langqin/Desktop/m2m_Sub001',  # m2m文件路径
        r=10,  # roi半径
        roi=[13.8, 1.3, 11.9],  # roi坐标
        max_workers=5  # 线程数
    )