import threading
import multiprocessing
import time


def cpu_tense(number):
    """计算质数"""

    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return 0
    return 1


def count_zs(counts):
    """计算固定数量的质数"""
    # 模拟CPU密集型
    initial_number = 2
    total_zs = 0
    while total_zs <= counts:
        total_zs += cpu_tense(initial_number)
        initial_number += 1
    return initial_number


if __name__ == '__main__':
    times = 100000

    # 同步
    t1 = time.time()
    count_zs(times)
    count_zs(times)
    count_zs(times)
    count_zs(times)
    print("CPU密集型下同步所需要的时间：", time.time() - t1)

    # 多线程
    t2 = time.time()
    threading_list = [threading.Thread(target=count_zs, args=(times,)) for _ in range(4)]
    for thread in threading_list:
        thread.start()
    for thread in threading_list:
        thread.join()  # 阻塞主进程
    print("CPU密集型下多线程所需要的时间：", time.time() - t2)

    # 多进程
    t3 = time.time()
    process_list = [multiprocessing.Process(target=count_zs, args=(times,)) for _ in range(4)]
    for process in process_list:
        process.start()
    for process in process_list:
        process.join()  # 阻塞主进程
    print("CPU密集型下多进程所需要的时间：", time.time() - t3)

    # 进程池
    t4 = time.time()
    pool = multiprocessing.Pool(processes=4)
    pool_output = pool.map(count_zs, [100000 for _ in range(4)])
    pool.close()
    pool.join()
    print("CPU密集型下进程池所需要的时间：", time.time() - t4)
