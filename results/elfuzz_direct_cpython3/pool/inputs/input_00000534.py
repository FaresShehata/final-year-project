"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          type checking with mypy and blacken-docs + pyright

This is a seed script that you can copy from to your own project. Just change the package name.
"""

import ast
from concurrent import futures
import multiprocessing as mp
import threading
import sys
import argparse
import time

# Import the necessary modules for concurrency, string parsing, and type hinting.

def fibonacci(n):
    if n <= 1:
        return n
    else:
        return(fibonacci(n-1) + fibonacci(n-2))

def thread_function():
    """Thread function."""
    print("Thread started")
    for i in range(4):
        # Pause execution for 1 second before starting next loop iteration
        time.sleep(1)
        print(i)

def process_function():
    """Process function."""
    print("Process started")
    for i in range(4):
        # Pause execution for 1 second before starting next loop iteration
        time.sleep(1)
        print(i)


def main(args: argparse.Namespace):
    """Main entry point of this program."""

    # TODO: Add code here that uses threads or processes to calculate Fibonacci numbers.
    
    # Create two threads 
    t1 = threading.Thread(target=thread_function)
    t2 = threading.Thread(target=process_function)
  
    # Start both threads 
    t1.start() 
    t2.start()

    # Wait until both threads have finished their work
    t1.join()
    t2.join()

    # Print the final result of Fibonacci sequence
    print("Fibonacci sequence up to 4:")
    for i in range(10):
        print(fibonacci(i))


    # TODO: Add code here that calculates Fibonacci numbers using a pool of processes.
    # TODO: Add code here that calculates Fibonacci numbers using a pool of threads.

    # Get the current date and time
    now = time.localtime(time.time())
    year = int(now.tm_year)
    month = int(now.tm_mon)
    day = int(now.tm_mday)
    hour = int(now.tm_hour)
    minute = int(now.tm_min)

    # Calculate the number of seconds since midnight
    elapsed_seconds = (hour * 3600) + (minute * 60)

    # Check if it's past midnight
    if elapsed_seconds >= 86400:
        # It's past midnight, so reset the clock
        year += 1
        month = 1
        day = 1
        hour = 0
        minute = 0
    
    # Convert the elapsed minutes back into hours and minutes
    elapsed_hours = elapsed_seconds // 3600
    elapsed_minutes = (elapsed_seconds % 3600) // 60

    # Print out the new date and time
    print(f"{year}/{month}/{day} {hour}:{minute}")

    # TODO: Add code here that measures the performance of Fibonacci calculations using a pool of processes.


    # Get the start time
    start_time = time.time()

    # Make a list of arguments for our Fibonacci function
    args_list = [(i,) for i in range(10)]

    # Use the ThreadPoolExecutor class to run multiple tasks concurrently
    executor = mp.Pool(processes=4)
    results = [executor.apply_async(func=fibonacci, args=args) for args in args_list]
    # Close the pool and wait for all tasks to complete
    executor.close()
    executor.join()

    # Get the end time
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time} seconds")

if __name__ == "__main__":
    main(sys.argv[1:])