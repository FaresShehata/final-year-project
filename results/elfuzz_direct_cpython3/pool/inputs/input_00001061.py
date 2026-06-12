"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter), 
          exception handling (contextlib)
"""

"""Thread vs. Process
    Threads share same memory space.
    Good for CPU-bound tasks.
        - Inefficient to use for I/O-bound tasks.

    Processes have separate memory spaces.
    Better for IO-bound tasks.
        - Can be used for CPU-bound tasks as well if they're not too heavy on the system.

    Multiprocessing vs. Multithreading
        - Multiprocessing is better when you want to make sure that processes run in parallel rather than threads.
            - This is because threads are shared by all other processes running under your process group.
            - Process groups can communicate through inter-process communication mechanisms like pipes and sockets.
            - Processes can also synchronize with one another using synchronization primitives such as locks, semaphores, condition variables etc., which are platform dependent.
        - Multiprocessing is a bit slower than multithreading but it provides the maximum isolation between processes if any one of them fails or crashes then the impact would be minimal since each process has its own private memory space.
        - In general, multiprocessing is preferred over multithreading when you need full control over what happens at every point in time, whether it be data access, system calls or even just simple memory manipulation.
        - But in case of multi-threaded programming, we do not have this kind of control. All the threads share the same memory space and so any thread could potentially crash and cause data corruption across all other threads.
"""


import json
from contextlib import redirect_stdout
import threading
from time import sleep

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

print("Welcome to the baby names parser!")

while True:
    try:
        file_path = input("Please enter path to the JSON file containing data about baby names:\n")
        with open(file_path) as f:
            names_data = json.load(f)

            break
    except FileNotFoundError:
        print("File was not found!")
    except json.JSONDecodeError:
        print("JSON parse error!")

names_by_gender_dict = {}
for name_list in names_data['data']:
    gender = name