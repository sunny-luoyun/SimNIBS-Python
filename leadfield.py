import os.path
import time
from simnibs import sim_struct, run_simnibs
def leadfieldbuild():
    while True:
        subpath = input('输入被试文件夹(m2m文件夹)')
        print('被试文件夹为：',subpath)
        choice = input('回车继续，输入0返回上一步')
        if choice == '':
            break
        elif choice == '0':
            continue
    output = os.path.join(subpath,'leadfield')
    st = time.time()
    tdcs_lf = sim_struct.TDCSLEADFIELD()
    # subject folder
    tdcs_lf.subpath = subpath
    # output directory
    tdcs_lf.pathfem = output
    # Uncoment to use the pardiso solver
    tdcs_lf.solver_options = 'pardiso'
    # This solver is faster than the default. However, it requires much more
    # memory (~12 GB)
    run_simnibs(tdcs_lf)
    print('索引建立结束')
    et = time.time()
    elapsed_time = et - st
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)
    print(f"处理结束，共花费时间：{hours}小时{minutes}分{seconds}秒")

