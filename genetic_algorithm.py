import random
import os
import pickle
import concurrent.futures
import TI

# 电极位置列表
electrode_positions = [
    'Fp1', 'Fp2', 'Fz', 'F3', 'F4', 'F7', 'F8', 'Cz', 'C3', 'C4', 'T7', 'T8',
    'Pz', 'P3', 'P4', 'P7', 'P8', 'O1', 'O2', 'Fpz', 'AFz', 'AF3', 'AF4', 'AF7',
    'AF8', 'F1', 'F2', 'F5', 'F6', 'FCz', 'FC1', 'FC2', 'FC3', 'FC4', 'FC5', 'FC6',
    'FT7', 'FT8', 'C1', 'C2', 'C5', 'C6', 'CPz', 'CP1', 'CP2', 'CP3', 'CP4', 'CP5',
    'CP6', 'TP7', 'TP8', 'P1', 'P2', 'P5', 'P6', 'POz', 'PO3', 'PO4', 'PO7', 'PO8',
    'Oz'
]

# 初始化种群
def initialize_population(population_size, electrode_positions, num_electrodes):
    population = set()
    while len(population) < population_size:
        individual = tuple(sorted(random.sample(electrode_positions, num_electrodes)))
        population.add(individual)
    return list(population)

# 计算适应度（多核版本）
def calculate_fitness(population, log_file, path, r, roi, fitness_cache, max_workers=None):
    fitness = [0] * len(population)  # 初始化适应度列表
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, individual in enumerate(population):
            if individual in fitness_cache:
                fitness[idx] = fitness_cache[individual]
                log_file.write(
                    f"Using cached fitness for combination {idx + 1}: {individual} -> Field Strength: {fitness_cache[individual]}\n")
                log_file.flush()
            else:
                # 提交任务时传递索引和电极组合
                futures.append(executor.submit(TI.calculate_electric_field, *individual, path, r, roi, idx))

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                idx = result[0]  # 获取返回的索引
                fitness_value = result[1]  # 获取返回的适应度值
                fitness[idx] = fitness_value
                fitness_cache[individual] = fitness_value
                log_file.write(f"Trying combination {idx + 1}: {population[idx]} -> Field Strength: {fitness_value}\n")
                log_file.flush()
            except Exception as e:
                log_file.write(f"Error occurred while calculating fitness for combination {idx + 1}: {population[idx]}\n")
                log_file.write(f"Error: {e}\n")
                log_file.flush()
                fitness[idx] = 0  # 如果出错，将适应度值设为 0
    return fitness

# 轮盘赌选择
def selection(population, fitness, elite_size, log_file):
    total_fitness = sum(fitness)
    if total_fitness == 0:
        log_file.write("Total fitness is zero. Returning current population.\n")
        log_file.flush()
        return population

    selection_probs = [f / total_fitness for f in fitness]
    selected_indices = random.choices(range(len(population)), weights=selection_probs, k=len(population) - elite_size)
    selected_population = [population[i] for i in selected_indices]
    elite_indices = sorted(range(len(fitness)), key=lambda i: fitness[i], reverse=True)[:elite_size]
    elite_population = [population[i] for i in elite_indices]
    return selected_population + elite_population

# 单点交叉操作
def crossover(selected_population, crossover_rate):
    offspring = []
    for i in range(0, len(selected_population), 2):
        if random.random() < crossover_rate:
            crossover_point = random.randint(1, len(selected_population[0]) - 1)
            parent1 = list(selected_population[i])
            parent2 = list(selected_population[i + 1])
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            offspring.append(tuple(sorted(child1)))
            offspring.append(tuple(sorted(child2)))
        else:
            offspring.append(selected_population[i])
            if i + 1 < len(selected_population):
                offspring.append(selected_population[i + 1])
    return offspring

# 变异操作
def mutation(population, mutation_rate, electrode_positions):
    mutated_population = []
    for individual in population:
        if random.random() < mutation_rate:
            mutation_point = random.randint(0, len(individual) - 1)
            new_individual = list(individual)
            while True:
                new_electrode = random.choice(electrode_positions)
                if new_electrode not in new_individual:
                    new_individual[mutation_point] = new_electrode
                    break
            mutated_population.append(tuple(sorted(new_individual)))
        else:
            mutated_population.append(individual)
    return mutated_population

# 保存种群状态
def save_population_state(population, fitness, generation, fitness_cache, checkpoint_file):
    with open(checkpoint_file, 'wb') as f:
        pickle.dump((population, fitness, generation, fitness_cache), f)

# 加载种群状态
def load_population_state(path):
    checkpoint_file = os.path.join(path, "checkpoint.pkl")
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'rb') as f:
            population, fitness, generation, fitness_cache = pickle.load(f)
        return population, fitness, generation, fitness_cache
    return None, None, 0, {}

# 主程序
def genetic_algorithm(population_size, max_generations, crossover_rate, mutation_rate, fitness_threshold, elite_size,
                      path, r, roi, max_workers=None):
    log_file_path = os.path.join(path, "results.txt")
    checkpoint_file = os.path.join(path, "checkpoint.pkl")
    fitness_cache = {}  # 用于缓存适应度值
    with open(log_file_path, 'a') as log_file:
        log_file.write("Starting genetic algorithm...\n")
        log_file.flush()

        # 尝试加载上次的种群状态
        population, fitness, start_generation, fitness_cache = load_population_state(path)
        if population is None:  # 如果没有检查点文件，则初始化种群
            population = initialize_population(population_size, electrode_positions, 4)
            start_generation = 0

        # 主循环
        for generation in range(start_generation, max_generations):
            log_file.write(f"\nGeneration {generation + 1}:\n")
            log_file.flush()

            # 计算适应度
            fitness = calculate_fitness(population, log_file, path, r, roi, fitness_cache, max_workers)

            # 打印当前尝试的次数和最佳组合
            best_individual = population[fitness.index(max(fitness))]
            log_file.write(f"Best combination: {best_individual}, Fitness: {max(fitness)}\n")
            log_file.flush()

            # 检查是否达到适应度阈值
            if max(fitness) >= fitness_threshold:
                log_file.write(
                    f"Reached the fitness threshold of {fitness_threshold} in {generation + 1} generations.\n")
                log_file.flush()
                break

            # 选择
            selected_population = selection(population, fitness, elite_size, log_file)

            # 交叉
            offspring = crossover(selected_population, crossover_rate)

            # 变异
            population = mutation(offspring, mutation_rate, electrode_positions)

            # 保存当前状态到检查点文件
            save_population_state(population, fitness, generation + 1, fitness_cache, checkpoint_file)

        # 输出最优解
        best_individual = population[fitness.index(max(fitness))]
        log_file.write("\nFinal result:\n")
        log_file.write(f"Optimal electrode combination: {best_individual}\n")
        log_file.write(f"Electric field strength: {max(fitness)}\n")
        log_file.flush()

if __name__ == "__main__":
    genetic_algorithm(
        population_size=50,  # 种群大小
        max_generations=200,  # 最大代数
        crossover_rate=0.8,  # 交叉率
        mutation_rate=0.1,  # 变异率
        fitness_threshold=3.0,  # 适应度阈值
        elite_size=3,  # 精英保留数量
        path='/Users/langqin/Desktop/m2m_Sub001',  # m2m文件路径
        r=10, # roi半径
        roi=[11.7, -2.4, -6.1], # roi坐标
        max_workers=50 # 线程数
    )
