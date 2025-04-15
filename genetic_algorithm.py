import random
import os
import pickle  # 用于保存和加载种群状态
import single_ti
# 假设的电极位置列表（10-10系统中的64个电极位置）
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

# 计算适应度
def calculate_fitness(population, log_file, path, r, roi, fitness_cache):
    fitness = []
    for idx, individual in enumerate(population):
        if individual in fitness_cache:
            fitness_value = fitness_cache[individual]
        else:
            e1, e2, e3, e4 = individual
            fitness_value = single_ti.sim(e1, e2, e3, e4, path, r, roi)
            fitness_cache[individual] = fitness_value
        log_file.write(f"Trying combination {idx + 1}: {individual} -> Field Strength: {fitness_value}\n")
        log_file.flush()
        fitness.append(fitness_value)
    return fitness

# 轮盘赌选择
def selection(population, fitness, elite_size):
    total_fitness = sum(fitness)
    selection_probs = [f / total_fitness for f in fitness]
    selected_indices = random.choices(range(len(population)), weights=selection_probs, k=len(population) - elite_size)
    selected_population = [population[i] for i in selected_indices]
    elite_indices = sorted(range(len(fitness)), key=lambda i: fitness[i], reverse=True)[:elite_size]
    elite_population = [population[i] for i in elite_indices]
    return selected_population + elite_population

# 交叉操作
def crossover(population, crossover_rate):
    offspring = set()
    while len(offspring) < len(population):
        parent1, parent2 = random.sample(population, 2)
        if random.random() < crossover_rate:
            crossover_point = random.randint(1, len(parent1) - 1)
            child1 = tuple(sorted(parent1[:crossover_point] + parent2[crossover_point:]))
            child2 = tuple(sorted(parent2[:crossover_point] + parent1[crossover_point:]))
            offspring.add(child1)
            offspring.add(child2)
        else:
            offspring.add(parent1)
            offspring.add(parent2)
    return list(offspring)

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
def load_population_state(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'rb') as f:
            population, fitness, generation, fitness_cache = pickle.load(f)
        return population, fitness, generation, fitness_cache
    return None, None, 0, {}

# 主程序
def genetic_algorithm(population_size, max_generations, crossover_rate, mutation_rate, fitness_threshold, elite_size, path, r, roi, checkpoint_file):
    log_file_path = os.path.join(path, "results.txt")
    fitness_cache = {}  # 用于缓存适应度值
    with open(log_file_path, 'a') as log_file:
        log_file.write("Starting genetic algorithm...\n")
        log_file.flush()

        # 尝试加载上次的种群状态
        population, fitness, start_generation, fitness_cache = load_population_state(checkpoint_file)
        if population is None:  # 如果没有检查点文件，则初始化种群
            population = initialize_population(population_size, electrode_positions, 4)
            start_generation = 0

        # 主循环
        for generation in range(start_generation, max_generations):
            log_file.write(f"\nGeneration {generation + 1}:\n")
            log_file.flush()

            # 计算适应度
            fitness = calculate_fitness(population, log_file, path, r, roi, fitness_cache)

            # 打印当前尝试的次数和最佳组合
            best_individual = population[fitness.index(max(fitness))]
            log_file.write(f"Best combination: {best_individual}, Fitness: {max(fitness)}\n")
            log_file.flush()

            # 检查是否达到适应度阈值
            if max(fitness) >= fitness_threshold:
                log_file.write(f"Reached the fitness threshold of {fitness_threshold} in {generation + 1} generations.\n")
                log_file.flush()
                break

            # 选择
            selected_population = selection(population, fitness, elite_size)

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
    checkpoint_file = "/Users/langqin/Desktop/m2m_Sub001/checkpoint.pkl"  # 检查点文件路径
    genetic_algorithm(
        population_size=20,
        max_generations=200,
        crossover_rate=0.6,
        mutation_rate=0.2,
        fitness_threshold=3.0,
        elite_size=5,
        path='/Users/langqin/Desktop/m2m_Sub001',
        r=5,
        roi=[0, 0, 0],
        checkpoint_file=checkpoint_file
    )