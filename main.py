import os,genetic_algorithm
import subprocess
import leadfield
import opt
import single_ti
import pair_algorithm
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

def get_user_input():
    while True:
        path = input("请输入文件路径: ").strip()
        if os.path.exists(path):
            folder_name = os.path.basename(path)
            if folder_name.startswith("m2m_"):
                xxx = folder_name[4:]
                print(f"处理的被试为: {xxx}")
                break
            else:
                print("路径不符合预期格式，请输入以 'm2m_' 开头的文件夹路径。")
        else:
            print("路径无效，请重新输入。")

    while True:
        roi = input("请输入ROI的个体空间坐标（用逗号或空格分隔）: ").strip()
        try:
            roi_list = [float(coord) for coord in roi.replace(',', ' ').split()]
            if len(roi_list) == 3:  # 假设ROI坐标是三维的
                print(f"输入的ROI坐标为: {roi_list}")
                break
            else:
                print("ROI坐标必须包含3个数值，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入数字，用逗号或空格分隔。")

    while True:
        try:
            r = float(input("请输入半径: ").strip())
            if r > 0:
                break
            else:
                print("半径必须为正数，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入一个数字。")

    while True:
        try:
            e = float(input("请输入电场大小: ").strip())
            if e > 0:
                break
            else:
                print("电场大小必须为正数，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入一个数字。")

    return path, roi_list, r, e

def get_roi_field():
    while True:
        path = input("请输入文件路径: ").strip()
        if os.path.exists(path):
            folder_name = os.path.basename(path)
            if folder_name.startswith("m2m_"):
                xxx = folder_name[4:]
                print(f"处理的被试为: {xxx}")
                break
            else:
                print("路径不符合预期格式，请输入以 'm2m_' 开头的文件夹路径。")
        else:
            print("路径无效，请重新输入。")

    while True:
        roi = input("请输入ROI的个体空间坐标（用逗号或空格分隔）: ").strip()
        try:
            roi_list = [float(coord) for coord in roi.replace(',', ' ').split()]
            if len(roi_list) == 3:  # 假设ROI坐标是三维的
                print(f"输入的ROI坐标为: {roi_list}")
                break
            else:
                print("ROI坐标必须包含3个数值，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入数字，用逗号或空格分隔。")

    while True:
        try:
            r = float(input("请输入半径: ").strip())
            if r > 0:
                break
            else:
                print("半径必须为正数，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入一个数字。")

    while True:
        try:
            e1 = input('请输入通道1，第1个电极位置(10-10EEG):')
            e2 = input('请输入通道1，第2个电极位置(10-10EEG):')
            e3 = input('请输入通道2，第1个电极位置(10-10EEG):')
            e4 = input('请输入通道2，第2个电极位置(10-10EEG):')
            break
        except:
            pass

    return e1,e2,e3,e4,path,r,roi_list


def run_genetic_algorithm(path, roi_list, r, e):
    print("\n正在运行遗传算法，参数如下：")
    print(f"路径: {path}")
    print(f"ROI坐标: {roi_list}")
    print(f"半径: {r}")
    print(f"电场大小: {e}")
    print("遗传算法正在运行，请稍候...")

    genetic_algorithm.genetic_algorithm(
        population_size=50,
        max_generations=200,
        crossover_rate=0.6,
        mutation_rate=0.2,
        fitness_threshold=e,
        elite_size=3,
        path=path,
        r=r,
        roi=roi_list
    )

    print("遗传算法运行完成！")

def main():
    check_for_updates()
    while True:
        choice = input('输入1进行索引建立\n输入2TI逆向(全电极位)\n输入3TI逆向(坐标位)\n输入4进行roi处电场查看\n输入5TI逆向(对称电极位)')
        if choice == '1':
            leadfield.leadfieldbuild()
            break
        elif choice == '2':
            path, roi_list, r, e = get_user_input()
            run_genetic_algorithm(path, roi_list, r, e)
            break
        elif choice == '3':
            path, roi_list, r, e = get_user_input()
            opt.opt(path,roi_list,r,e)
            break
        elif choice == '4':
            e1,e2,e3,e4,path,r,roi = get_roi_field()
            (idx, e) = single_ti.sim(e1,e2,e3,e4,path,r,roi,idx=None)
            print(f'roi处平均电场为 {e} V/m')
            break
        elif choice == '5':
            path, roi_list, r, e = get_user_input()
            num_pairs = 2
            pair_algorithm.exhaustive_search(num_pairs,path,r, roi_list, max_workers=50)
            break


if __name__ == "__main__":
    main()