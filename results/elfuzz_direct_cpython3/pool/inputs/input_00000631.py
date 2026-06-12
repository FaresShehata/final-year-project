"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never, Unpack), 
          dataclasses
"""

import sys

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import multiprocessing
from functools import lru_cache, cache
from timeit import default_timer as timer
from contextlib import contextmanager


# Scenario 1 - Threading and Multiprocessing
def scenario_1():
    """Scenario 1 - Threading and Multiprocessing"""
    
    # Start the timers for each scenario
    start_time = timer()
    
    def print_hello_world(number_of_times):
        for _ in range(number_of_times):
            print("Hello, World!")
            
    # Create thread pool executor for threading
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(print_hello_world, number_of_times) for number_of_times in range(2)]
        
        # Wait for all threads to complete before moving on to Scenario 2
        for future in futures:
            future.result()

    # Stop the timer after both scenarios are completed
    end_time_threadpool = timer() - start_time
    
    print(f"Thread Pool Completed in {end_time_threadpool:.6f} seconds")
    
    
    # Create process pool executor for multiprocessing
    start_time = timer()
    
    def print_hello_world_multiprocess(number_of_times):
        for _ in range(number_of_times):
            print("Hello, World from a different thread!")
    
    with ProcessPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(print_hello_world_multiprocess, number_of_times) for number_of_times in range(2)]
        
        # Wait for all processes to complete before moving on to Scenario 3
        for future in futures:
            future.result()

    # Stop the timer after both scenarios are completed
    end_time_processpool = timer() - start_time
    
    print(f"Process Pool Completed in {end_time_processpool:.6f} seconds")


# Scenario 2 - Concurrency with ExecutorService
def scenario_2():
    """Scenario 2 - Concurrency with ExecutorService"""
    
    # Scenario 2a - ThreadPoolExecutor
    start_time = timer()
    
    def worker_function(name):
        return f"{name}: Hello from a thread!"
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(worker_function, ["Alice", "Bob"])
        
    end_time_thread_pool_executor = timer() - start_time
    
    print("\nResults using ThreadPoolExecutor:")
    for result in	]
	def annotated_func(person: Person