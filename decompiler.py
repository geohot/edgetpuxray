#!/usr/bin/env python3
import struct
import ctypes
from hexdump import hexdump
from construct import BitStruct, BitsInteger
from collections import defaultdict

dat = open("programs/div2.coral", "rb").read()

#def fix(y):
#  return bytes([int("0x"+x, 16) for x in y.split()])
#op = fix("00 08 00 00 00 00 C0 1B  00 AA AA AA AA 00 00 00")
#print(op)

ins = BitStruct(
  "unk_3" / BitsInteger(28),
  "imm_scalar" / BitsInteger(32),
  "unk_2" / BitsInteger(3),
  "s1_x" / BitsInteger(5),
  "unk_1" / BitsInteger(6),
  "imm_size" / BitsInteger(32),
  "prefix" / BitsInteger(22),
)
# TODO: can assert that it's 128?
assert ins.sizeof() == 16

def dec(my_dat):
  hexdump(my_dat)
  dd = ins.parse(my_dat[::-1])
  print(dd)

for i in range(0, 0x80, 0x10):
  dec(dat[i:i+0x10])

#for i in range(-0x40, -0x10, 0x10): dec(dat[i:i+0x10])
#dec(dat[-0x60:-0x50])
#dec(dat[-0x50:-0x40])
#dec(dat[-0x40:-0x30])
#dec(dat[-0x30:-0x20])
#dec(dat[-0x20:-0x10])
#dec(dat[-0x10:])

"""
for i in range(0, len(dat), 0x10):
  my_dat = dat[i:i+0x10]
  hexdump(my_dat)
  dd = ins.parse(my_dat[::-1])
  print(dd)
  if i == 0x80:
    break
"""

def mins(**kwargs):
  ret = defaultdict(lambda: 0)
  for k,v in kwargs.items():
    ret[k] = v
  return [ins.build(ret)[::-1]]

print("my program")
prog = []
prog += mins(prefix=2048, unk_1=47, s1_x=0, imm_scalar=0x1337)
prog += mins(prefix=2048, unk_1=47, s1_x=1, imm_scalar=0x1337)
prog += mins(prefix=2048, unk_1=47, s1_x=2, imm_scalar=0x1337)
prog += mins(prefix=2048, unk_1=47, s1_x=3, imm_scalar=0x1337)
prog += mins(prefix=67648) # halt

# add start at the end
prog = mins(prefix=3968, imm_size=len(prog)*0x10) + prog  # start
prog += mins(prefix=4032, imm_size=0x10)  # end
prog = b''.join(prog)
hexdump(prog)

with open("programs/custom.coral", "wb") as f:
  f.write(prog)