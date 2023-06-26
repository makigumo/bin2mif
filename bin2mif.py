#!/usr/bin/env python3

import os
import pathlib
import struct

import sys


class BinaryEOFException(Exception):
  def __init__(self):
    pass

  def __str__(self):
    return 'Premature end of file.'


class BinaryReader:

  def __init__(self, file_name):
    self.file = open(file_name, 'rb')

  def unpack(self, type_format):
    type_size = struct.calcsize(type_format)
    value = self.file.read(type_size)
    if type_size != len(value):
      raise BinaryEOFException
    return struct.unpack(type_format, value)[0]

  def __del__(self):
    self.file.close()


def header(width=8, depth=0):
  return """-- Quartus Prime generated Memory Initialization File (.mif)

WIDTH=%d;
DEPTH=%d;

ADDRESS_RADIX=HEX;
DATA_RADIX=HEX;

CONTENT BEGIN
""" % (width, depth)


def footer():
  return "END;\n"


def print_usage():
  print("Usage: %s <bin file>" % sys.argv[0])


if len(sys.argv) < 1:
  print_usage()
  exit(1)

source_filename = sys.argv[1]
binaryReader = BinaryReader(source_filename)
output_path = pathlib.Path.cwd()

try:
  width_in_bits = 8
  source_file_size = os.path.getsize(source_filename)
  if source_file_size == 0:
    print("Empty file.")
    exit(0)
  p = pathlib.Path(output_path).joinpath(source_filename + ".mif")
  os.makedirs(os.path.dirname(p), exist_ok=True)
  with p.open('w') as fh:
    fh.write(f"-- Converted from '{source_filename}'\n")
    fh.write(header(width_in_bits, source_file_size))
    pos_start = 0
    new_byte_value = binaryReader.unpack("B")
    i = 0
    try:
      while i < source_file_size - 1:
        next_byte_value = binaryReader.unpack("B")
        if new_byte_value != next_byte_value:
          fh.write(f"  {i:04X}  :   {new_byte_value:02X};\n")
        else:
          pos_start = i
          try:
            while new_byte_value == next_byte_value:
              i += 1
              next_byte_value = binaryReader.unpack("B")
          finally:
            fh.write(f"  [{pos_start:04X}..{i:04X}]  :   {new_byte_value:02X};\n")
        new_byte_value = next_byte_value
        i += 1
      else:
        fh.write(f"  {i:04X}  :   {new_byte_value:02X};\n")

    except BinaryEOFException:
      pass

    fh.write(footer())

except OSError:
  print("File error.")
