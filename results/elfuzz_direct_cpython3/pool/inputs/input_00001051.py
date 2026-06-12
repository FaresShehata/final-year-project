"""
Seed 03 — Functional programming: closures, higher-order functions, comprehensions,
          generators, coroutines (send/throw/close), itertools, functools,
          lambda calculus encoding, currying, partial application, trampolining, etc.
"""

import asyncio
from contextlib import asynccontextmanager
import re
import sys
from typing import List, Literal, NamedTuple, Optional, Tuple, TypeAlias, Union, get_args

sys.setrecursionlimit(500)

re.match(r"^(.+)(\d+)$", "hello")


@asynccontextmanager
async def open_connection(host='localhost', port=80):
    connection = await asyncio.open_connection(host, port)
    yield connection
    await connection.close()


async def read_until_eof(reader) -> str:
    data = await reader.read(1024)
    while len(data) > 0:
        if data.endswith(b'\n'):
            return data.decode('utf-8')
        else:
            data += await reader.read(1024)


async def main_v1() -> None:
    host = 'google.com'
    port = 80
    async with open_connection(host, port) as conn:
        reader, writer = conn
        writer.write(b'GET / HTTP/1.0\r\nHost: google.com\r\n\r\n')
        data = await read_until_eof(reader)
        print(f'Received {data!r}')


def parse_http_header(header_text: str) -> dict[str, str]:
    """Parse the headers from an HTTP response."""
    header_dict = {}
    # Splitting on \r\n is a bit more robust than splitting on '\n'.split()
    for row in header_text.split('\r\n'):
        key, value = map(str.strip, row.split(':', 1))
        header_dict[key] = value
    return header_dict


def parse_response(response_data: bytes) -> dict[Literal['status'], int]:
    """Return a dictionary containing the status code and reason phrase of an HTTP response."""
    http_version, status_code, status_reason = \
        next(re.findall(rb'^HTTP/\d+\.\d+\s(\d+)\s(.*)$', response_data))[0]
    return {
        'http_version': http_version.decode(),
        'status': int(status_code),
        'reason_phrase': status_reason.decode(),
    }


class HttpHeader(NamedTuple):
    host: str
    connection: Optional[str]


@asynccontextmanager
async def open_connection_with_headers(
        host: str, port: int, *, headers: HttpHeader = HttpHeader('', None)) -> AsyncGenerator[Tuple[bytes], None]:
    """
    Open a TCP connection to a server.

    Args:
      host: The hostname or IP address of the server.
      port: The port number of the server.
      headers: A NamedTuple specifying the HTTP headers to send with the request.

    Yields:
      A tuple containing the raw bytes of the response.
    """

    # Connect to the remote host
    reader, writer = await asyncio.open_connection(host, port)
    #    asyncio.run(main_v3())
    asyncio.run(main_v4())

# Python 3.9+
with open("file.txt") as f:
    async for line in f.async_iter_lines():
        print(line.strip())

# https://docs.python.org/3/library/itertools.html