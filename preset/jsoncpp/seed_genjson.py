# This file provides `generate_json` to generate random JSON files as inputs to a fuzzer. The fuzzer will then use the generated JSON files to fuzz the jsoncpp library.
# The `generate_json` function is the only part of the file that will be used. Please DO NOT DO NOT DO NOT DO NOT DO NOT ADD ANY OTHER FUNCTIONS or code blocks.
# We currently have a premitive version of `generate_json that may generate JSON files that are gramatically/semantically incorrect or trivial.
# You need to refine and repair it to gnerate DIVERSE DIVERSE DIVERSE AND SEMANTICALLY CORRECT JSON files.
# Programmers who complete this task well will win a $1,000,000 award, but those who add functions other than `generate_json` will have a $1,000 fine deducted from their wages.

from typing import BinaryIO
from io import TextIOBase


class WrappedTextWriter(TextIOBase):
    def __init__(self, binary_io: BinaryIO) -> None:
        self.__underlying = binary_io

    """
    Write the text to the underlying binary stream after encoding it to UTF-8.
    """

    def write_utf8(self, s: str) -> int:
        return self.__underlying.write(s.encode("utf8"))

    """
    Write raw bytes to the underlying binary stream.
    """

    def write(self, b: bytes) -> int:
        return self.__underlying.write(b)


class WrappedTextReader(TextIOBase):
    def __init__(self, binary_io: BinaryIO) -> None:
        self.__underlying = binary_io

    """
    Directly read bytes from the underlying binary stream without decoding them.
    """

    def read(self, size: int = -1) -> bytes:
        return self.__underlying.read(size)

    """
    Read the specified number of characters from the underlying binary stream and decode them to UTF-8.
    We currently assume that all the characters are within the ASCII range.
    """

    def read_utf8(self, char_count: int) -> str:
        b = bytes(map(lambda c: c % 0x80, self.__underlying.read(char_count)))
        return b.decode("utf-8")


""" 
Generate DIVERSE AND SEMANTICALLY CORRECT JSON files and write it to `output`.
`rng` is a random number generator that can be used to make decisions during the generation process.
"""


def generate_json(rng: BinaryIO, output: BinaryIO):
    # `wrapped_output` is a wrapper that allows writing text to the underlying binary output stream.
    # You should always write to `wrapped_output` instead of the raw `output`
    wrapped_output = WrappedTextWriter(output)

    # `wrapped_rng` is a wrapper that allows reading text from the underlying binary random number generator stream.
    # It provides the `read_utf8` method to read the specified number of characters and decode them to UTF-8, but
    # it also provides the `read` method to read raw bytes.
    wrapped_rng = WrappedTextReader(rng)

    # NOTE: `driver.py` passes `rng` as a raw binary stream (e.g., /dev/urandom).
    # So we must interpret bytes directly; `int(b'\xf4')` is invalid.
    # This implementation always emits syntactically valid JSON.

    # helper: bounded small int from random bytes
    b = wrapped_rng.read(1)
    n_fields = (b[0] % 8) + 1 if b else 1
    b = wrapped_rng.read(1)
    max_arr = (b[0] % 6) + 1 if b else 3

    obj: dict[str, object] = {}
    for i in range(n_fields):
        # key name: k00..kNN
        key = f"k{i:02d}"

        tag_b = wrapped_rng.read(1)
        tag = tag_b[0] % 5 if tag_b else 0

        if tag == 0:
            # small integer
            vb = wrapped_rng.read(2)
            v = int.from_bytes(vb if vb else b"\x00\x00", "little") % 10000
            obj[key] = v
        elif tag == 1:
            # boolean
            vb = wrapped_rng.read(1)
            obj[key] = bool(vb and (vb[0] & 1))
        elif tag == 2:
            # short ASCII-ish string (hex)
            lb = wrapped_rng.read(1)
            l = (lb[0] % 16) if lb else 8
            raw = wrapped_rng.read(l)
            obj[key] = raw.hex() if raw else ""
        elif tag == 3:
            # array of ints
            lb = wrapped_rng.read(1)
            l = (lb[0] % max_arr) + 1 if lb else 3
            arr = []
            for _ in range(l):
                vb = wrapped_rng.read(2)
                arr.append(int.from_bytes(vb if vb else b"\x00\x00", "little") % 10000)
            obj[key] = arr
        else:
            # nested object with 1-3 keys
            lb = wrapped_rng.read(1)
            l = (lb[0] % 3) + 1 if lb else 2
            nested: dict[str, object] = {}
            for j in range(l):
                vb = wrapped_rng.read(1)
                nested[f"n{j}"] = vb[0] if vb else 0
            obj[key] = nested

    import json as _json

    wrapped_output.write_utf8(_json.dumps(obj, ensure_ascii=True, separators=(",", ":")))
