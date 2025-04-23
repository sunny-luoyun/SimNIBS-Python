import os,genetic_algorithm
import subprocess
def check_for_updates():
    print("正在检查更新...")
    try:
        # 获取脚本所在的目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # 切换到脚本所在的目录
        os.chdir(script_dir)
        # 执行 git fetch 命令，获取远程仓库的最新状态
        subprocess.run(['git', 'fetch', '--quiet'], check=True)

        # 获取本地分支的最新提交哈希值
        local_commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            text=True
        ).strip()

        # 获取远程分支的最新提交哈希值
        remote_commit = subprocess.check_output(
            ['git', 'rev-parse', 'origin/main'],
            text=True
        ).strip()

        # 获取本地分支和远程分支的共同祖先提交哈希值
        common_ancestor = subprocess.check_output(
            ['git', 'merge-base', 'HEAD', 'origin/main'],
            text=True
        ).strip()

        # 比较本地提交和远程提交
        if local_commit == remote_commit:
            print("当前代码已是最新版本。")
        elif common_ancestor == local_commit:
            print("检测到更新！本地分支落后于远程分支。")
            choice = input("是否更新到最新版本？(y/n): ").strip().lower()
            if choice == 'y':
                print("正在更新...")
                # 执行 git pull 命令，更新代码
                subprocess.run(['git', 'pull'], check=True)
                print("更新完成！请重新运行程序。")
                exit(0)  # 更新完成后退出程序
            else:
                print("已跳过更新。")
        else:
            print("无法确定更新状态，请手动检查。")
    except subprocess.CalledProcessError as e:
        print(f"检查更新时出错：{e}")
    except Exception as e:
        print(f"发生错误：{e}")

check_for_updates()
# 路径输入
path = input("输入文件")
folder_name = os.path.basename(path)

if folder_name.startswith("m2m_"):
    # 提取 "m2m_" 之后的部分
    xxx = folder_name[4:]
    print("处理的被试为:", xxx)
else:
    print("路径不符合预期格式")
roi = input('输入ROI的个体空间坐标:')
roi_list = [float(coord) for coord in roi.replace(',', ' ').split()]
print('输入ROI为',roi_list)
r = input('输入半径')
r = float(r)
e = input('输入电场大小')
e = float(e)
# 函数运行
genetic_algorithm.genetic_algorithm(
        population_size=50,
        max_generations=200,
        crossover_rate=0.6,
        mutation_rate=0.2,
        fitness_threshold=e,
        elite_size=3,
        path = path,
        r = r,
        roi = roi_list
    )