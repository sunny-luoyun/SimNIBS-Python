import json, os
from charm import cut

def load_specific_parameters(file_path, *keys):
    try:
        with open(file_path, "r") as file:
            parameters = json.load(file)
        specific_params = {key: parameters[key] for key in keys if key in parameters}

        if len(specific_params) == 1:
            return list(specific_params.values())[0]
        else:
            return specific_params
    except FileNotFoundError:
        print(f"文件 {file_path} 未找到！")
        return {}
    except json.JSONDecodeError:
        print(f"文件 {file_path} 格式错误！")
        return {}


def menu():
    print("\n======== 以下是dwi批量处理界面 ========")
    print("1. 分割脑区")
    print("2. 逆算模拟")
    print("3. 使用说明")
    print("0. 退出程序")
    print("=====================================")


def get_input_path():
    while True:
        input_path = input('请输入工作路径(输入0返回上一级): ')
        if input_path == "0":
            return None
        try:
            full_path = os.path.join(input_path, 'pre')
            subjects = sorted(os.listdir(full_path))
            print(f'工作路径中有以下被试：')
            for subject in subjects:
                print(subject)
            return input_path, subjects
        except FileNotFoundError:
            print('请输入正确的路径!!!!')


def cut_brainarea(input_path, subjects):
    cut(input_path, subjects)


def help():
    print('---------------------使用说明------------------------------')
    print('工作路径为/home/xxx/xxx/workpath')
    print('工作路径下被试文件夹要求如下：')
    tree = """
    /home/xxx/xxx/workpath/pre
    │
    ├── Sub001
    │   ├── Sub001T1.nii.gz (结构像文件)
    │
    ├── Sub002
    │   ├── Sub002T1.nii.gz
    │
    ├── ...
    │
    └── Sub0xx
        ├── Sub0xxT1.nii.gz
        ├── Sub0xxdwi.json
        ├── Sub0xxdwi.bvec
        ├── Sub0xxdwi.bval
        ├── Sub0xxdwi.nii.gz
    注意每个文件及其名字的大小写！！！！！！！！！！
    """
    print(tree)
    input('按回车返回上一级')


def main():
    while True:
        menu()
        choice = input("请输入选项（0-3）：")
        if choice == "0":
            break
        elif choice in ["1", "2", "3", "0"]:
            input_path, subjects = get_input_path()
            if input_path is None:
                continue
            if choice == "1":
                cut_brainarea(input_path, subjects)
            elif choice == "2":
                pass
            elif choice == "3":
                help()
        else:
            print("无效的选项，请重新输入！")


if __name__ == "__main__":
    main()