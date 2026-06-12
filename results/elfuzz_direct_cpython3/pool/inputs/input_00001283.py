"""
Seed 05 — Concurrency (threading/multiprocessing/concurrent.futures),
          string parsing (ast.literal_eval, tokenize, textwrap, string.Formatter),
          typing extras (TypedDict, ParamSpec, Concatenate, TypeAlias, Never,
          Annotated, get_type_hints, reveal_type stub),
          __class_getitem__, __set_name__, __init_subclass__,
          contextlib (suppress, redirect_stdout, AbstractContextManager),
          numbers ABC, pathlib, tempfile, csv, base64, hashlib, hmac, secrets
"""
import asyncio
from concurrent import futures as cf
from functools import cached_property, lru_cache
import inspect
import io
import itertools
import logging
import re
import subprocess
import sys
from types import SimpleNamespace
import threading
import time

# TODO: https://docs.python.org/3/library/__future__.html
#   with nested_asyncio_contextmanager, nested_thread_contextmanager


def _log():
    for name in ('asyncio', 'multiprocessing'):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(name)s:%(levelname)s %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
    return logging.getLogger()


logger = _log()


class AsyncLoggerThread(threading.Thread):
    def run(self):
        while True:
            message = yield
            logger.debug(message)


def async_logger():
    thread = AsyncLoggerThread(target=_log, daemon=True)
    thread.start()
    return thread.put_nowait


async def async_log(message):
    await asyncio.sleep(1.0 / 20_000)
    await asyncio.create_task(async_logger()(message))


if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    async_loop.run_until_complete(async_log('hello'))
    async_loop.close()

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(async_log('bye'))
    finally:
        loop.close()