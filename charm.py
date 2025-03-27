import os, time

def cut(path, list):
    start_time = time.time()
    for i in list:
        start_timee = time.time()

        process = os.popen(
            f'mkdir -p {path}/work/preprocess/{i}')
        output = process.read()
        print(output)
        process.close()

        process = os.popen(f'charm {path}/work/preprocess/{i}/{i} {path}/pre/{i}/{i}T1.nii.gz --forceqform')
        output = process.read()
        print(output)
        process.close()

        # 记录结束时间
        end_time = time.time()
        elapsed_time = end_time - start_timee
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)

        print(f"处理{i}结束，共花费时间：{hours}小时{minutes}分{seconds}秒")

    end_time = time.time()
    elapsed_time = end_time - start_time
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    print(f"运行结束，共花费时间：{hours}小时{minutes}分{seconds}秒")