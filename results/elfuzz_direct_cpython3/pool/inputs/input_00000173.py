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

    # Parse arguments passed on command line
    parser = argparse.ArgumentParser(description="Run scripts concurrently using various methods.")
    parser.add_argument("--type", "-t", default=mp.Process, help="Type of concurrency to use.", choices=["processes", "threads"])
    args = parser.parse_args()
    
    start_time = time.time()

    if args.type == "threads":
        threads = [threading.Thread(target=thread_function) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    elif args.type == "processes":
        processes = [mp.Process(target=process_function) for _ in range(3)]
        for p in processes:
            p.start()
        for p in processes:
            p.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time taken: {total_time} seconds")

if __name__ == "__main__":
    main(sys.argv[1:])