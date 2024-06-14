# import multiprocessing as mp
# from multiprocessing import Pool
# import random
# import string

# # Define an output queue
# output = mp.Queue()

# # define a example function
# def rand_string(length, output):
#     """ Generates a random string of numbers, lower- and uppercase chars. """
#     rand_str = ''.join(random.choice(
#                     string.ascii_lowercase
#                     + string.ascii_uppercase
#                     + string.digits)
#                for i in range(length))
#     output.put(rand_str)

# # Setup a list of processes that we want to run
# processes = [mp.Process(target=rand_string, args=(5, output)) for x in range(4)]

# # Run processes
# for p in processes:
#     p.start()

# # Exit the completed processes
# for p in processes:
#     p.join()

# # Get process results from the output queue
# results = [output.get() for p in processes]

# print(results)

# print("Hi")
# def cube(x):
#     return x**3

# if __name__ == "__main__":
#     print("Start")
#     numbers = range(7)
#     p = Pool()
#     results = p.map(cube, range(1,7))
#     # results = p.map(cube, numbers)
#     print(results)

#     p.close()
#     p.join()


import os
import psutil
import time
import multiprocessing
from multiprocessing import Process, pool
import random

listIn = [int(0) for i in range(10000000)]
p = pool.ThreadPool(5)
CLOSE = False

def cpu_intensive_task(opt):
    # Simulate a CPU-intensive task
    # total = 0
    # print("in intensive task")
    # for i in range(len(opt)):
    opt += 1

    # for i in range(1, 10000000):
    #     total += (i * random.randint(0,999))
    # return total

def monitor_process(inputPID, threshold, interval):
# def monitor_process(threshold: int, interval: int):
    print("in process")
    print(f"os_pid: {os.getpid()}")
    process = psutil.Process(inputPID)

    # print("Ignore this")
    # Monitor the process for CPU usage
    while True:
        cpu_usage = process.cpu_percent(interval=interval)
        print(f"CPU usage: {cpu_usage}%")
        if cpu_usage > threshold:
            print("CPU usage threshold exceeded. Spawning a child process...")
            spawn_child_process()
            break
        time.sleep(interval)
    # pass

def spawn_child_process():
    # Define the function for the child process
    print("in child process")

    def child_task():
        print("Child process started")
        cpu_intensive_task()
        print("Child process finished")

    # Create and start a child process
    print("creating child process")
    child_process = multiprocessing.Process(target=child_task)
    print("created child process")

    child_process.start()
    # child_process.join()

def pool_task():
    global p
    global listIn
    print(f"p in task: {p}")
    x = 0
    while(True):
        if x > 5:
            p.close()
            p.terminate()
            p.join()
            print("closing")
            break
        print(f"pid check: {psutil.Process()}, CLOSE: {x}")
        p.map(cpu_intensive_task, listIn)
        x+=1
        
    print(f"exiting pool_task {p}")

    

if __name__ == "__main__":
    threshold = 75
    interval = 1

    # Get the current process
    current_process = psutil.Process().pid
    print(f"process: {current_process}")

    # monitor_process(current_process, threshold)
    # Start the monitoring in a separate process to avoid blocking
    # monitoring_process = Process(target=monitor_process(current_process, threshold, interval))
    # monitoring_process = multiprocessing.Process(target=monitor_process, args=(current_process, threshold,interval))

    # monitoring_process.start()
    # print(f"mp: {monitoring_process}, alive: {monitoring_process.is_alive()}")



    # Run the main CPU intensive task
    # p = pool.ThreadPool(5)
    print(f"p in main: {p}")
    pool_process = multiprocessing.Process(target=pool_task)
    print("Starting process")
    pool_process.start()

    print("Sleeping")
    time.sleep(10)

    print("Waking")
    # p.close()
    # p.terminate()
    # p.join()
    print(f"first: {listIn[0]} last: {listIn[-1]}") #-> this should not change since it is just a global var
    # p.close()
    
    # with pool.ThreadPool(5) as p:
        # while True:
        #     print(f"pid check: {psutil.Process()}")
        #     p.map(cpu_intensive_task)
    

    # Ensure the monitoring process finishes
    # monitoring_process.join()
