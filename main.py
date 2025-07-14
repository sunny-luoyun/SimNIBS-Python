import os,genetic_algorithm,charm
import time

from bs4.dammit import chardet_module

import opt
import single_ti
import pair_algorithm
import makeTISfile
'''
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
'''

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
            e = float(input("请输入roi处最小电场大小(V/m): ").strip())
            if e > 0:
                break
            else:
                print("电场大小必须为正数，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入一个数字。")

    while True:
        try:
            ma = float(input("请输入单通道电流大小(A): ").strip())
            if ma > 0:
                break
            else:
                print("电流大小必须为正数，请重新输入。")
        except ValueError:
            print("输入格式错误，请输入一个数字。")

    return path, roi_list, r, e, ma

def process_input(e):
    # 去除多余的空格
    e = e.strip()
    # 如果是10-10EEG脑电图的点位，直接返回
    if e.isalnum() and not e.isdigit() and not e.isalpha():
        return e
    # 如果是坐标
    else:
        # 按照空格分割
        coords = e.split()
        # 转换为浮点数
        coords = [float(coord) for coord in coords]
        # 转换为[x,y,z]的形式
        return coords

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
            e1 = input('请输入通道1，第1个电极位置(10-10EEG或坐标):')
            e1 = process_input(e1)
            e2 = input('请输入通道1，第2个电极位置(10-10EEG或坐标):')
            e2 = process_input(e2)
            e3 = input('请输入通道2，第1个电极位置(10-10EEG或坐标):')
            e3 = process_input(e3)
            e4 = input('请输入通道2，第2个电极位置(10-10EEG或坐标):')
            e4 = process_input(e4)
            break
        except ValueError:
            print("输入格式错误，请重新输入。")
        except Exception as e:
            print(f"发生错误：{e}")
            print("请重新输入。")

    while True:
        try:
            ma = input('请输入单通道电流大小(A):')
            ma = float(ma)
            break
        except ValueError:
            print("输入格式错误，请重新输入。")

    return e1,e2,e3,e4,path,r,roi_list, ma

def run_genetic_algorithm(path, roi_list, r, e, ma):
    print("\n正在运行遗传算法，参数如下：")
    print(f"路径: {path}")
    print(f"ROI坐标: {roi_list}")
    print(f"半径: {r}")
    print(f"预估电场大小: {e}")
    print(f'电流大小{ma}')
    print("遗传算法正在运行，请稍候...")
    time.sleep(10)

    genetic_algorithm.genetic_algorithm(
        population_size=50,
        max_generations=200,
        crossover_rate=0.6,
        mutation_rate=0.2,
        fitness_threshold=e,
        elite_size=3,
        path=path,
        r=r,
        roi=roi_list,
        ma = ma
    )

    print("遗传算法运行完成！")

def main():
    # check_for_updates()
    while True:
        choice = input('输入1进行T1像建模\n输入2TI逆向(得到EEG10-10的结果)\n输入3TI逆向(得到坐标点结果)\n输入4进行roi处电场查看\n输入5TI正向(对称电极位模拟)\n输入6进行一次TI模拟并生成模拟文件\n输入7查看各选项功能及用法\n输入0退出程序')
        if choice == '1':
            charm.charm()
            break
        elif choice == '2':
            path, roi_list, r, e, ma = get_user_input()
            run_genetic_algorithm(path, roi_list, r, e, ma)
            break
        elif choice == '3':
            path, roi_list, r, e, ma = get_user_input()
            opt.opt(path,roi_list,r,e, ma)
            break
        elif choice == '4':
            e1,e2,e3,e4,path,r,roi,ma = get_roi_field()
            (idx, e) = single_ti.sim(e1,e2,e3,e4,path,r,roi,ma,idx=None)
            print(f'CH1:{e1}-{e2}\n'
                  f'CH2:{e3}-{e4}\n'
                  f'电流大小为:{ma}A\n'
                  f'{roi}处半径{r}mm的小球内平均电场为{e}V/m')
            break
        elif choice == '5':
            path, roi_list, r, e, ma = get_user_input()
            num_pairs = 2
            pair_algorithm.exhaustive_search(num_pairs,path,r, roi_list, ma, max_workers=50)
            break
        elif choice == '6':
            e1, e2, e3, e4, path, r, roi, ma = get_roi_field()
            makeTISfile.sim(e1, e2, e3, e4, path, r, roi, ma, idx=None)

            break
        elif choice == '7':
            print('\n'
                  '本软件是调用SimNIBS进行TI刺激的仿真模拟。仿真模拟一共分为建模和模拟两个步骤\n\n'
                  '选项1：即为结构像的建模，需要输入原始结构像的NIFTI格式的文件（.nii）或包含DICOM格式（.dcm）的文件夹路径，以及输出路径，和被试编号(如:Subxxx)。\n'
                  '      如果为NIFTI格式的文件则程序会直接进行建模，若为DICOM格式的文件夹则程序会先将格式转换为NIFTI格式的文件再进行建模。\n'
                  '      建模后的文件会在输出路径里建立名字为：m2m_Subxxx的文件夹，之后的所有仿真模拟所需要输入的文件夹路径均为这个生成的m2m_Subxxx的文件夹。\n\n'
                  
                  '选项2：TI逆向，广义上来说这算是TI的正向模拟，将10-10EEG的所有电极点位的结果都计算一遍，但通过算法优化，将数十万次的尝试次数尽量缩减,最终得到电极点位下最佳的组合\n'
                  '      由于是算法优化，所以并不会真正穷举所有的点位结果，因此不能保证结果就是最优情况，最终得到的结果是电极点位的10-10EEG点位\n'
                  '      最终模拟的结果在results.txt中可进行查看\n\n'
                  ''
                  '选项3：TI逆向，与选项2不同，该方法是SimNIBS官方所给出的无电极位的真逆向模拟，最终得到的结果是电极点位的坐标\n'
                  '      最终模拟的结果在tes_optimize_ti_focality文件夹中的summary.txt中可进行查看\n\n'
                  ''
                  '选项4：查看roi处电场，该功能是对模拟的结果进行检验，也可以当作是单次的正向模拟。\n'
                  '      通过输入m2m_Subxxx的文件夹以及电极位置和想查看的roi的坐标和半径，即可查看该被试在设定的电流大小和电极位置下roi处的平均电场大小\n\n'
                  ''
                  '选项5：TI正向，该方法与选项2的方法相同，即通过正向模拟来获得最佳的电极点位放置方法，但该方法每对电极对都是左右脑对称放置\n'
                  '      这种对称放置的方法能大大减少正向模拟的尝试次数，故可以不用算法优化便能完成所有可能的放置情况模拟\n'
                  '      最终模拟的结果在pair_results.txt中可进行查看\n'
                  '选项6：生成单次模拟的文件。')
            input('回车返回')

        elif choice == '0':
            break


if __name__ == "__main__":
    main()