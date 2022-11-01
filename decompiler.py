#!/usr/bin/env python3
import struct
import ctypes
from hexdump import hexdump
from construct import BitStruct, BitsInteger
from collections import defaultdict

dat = open("programs/div2.coral", "rb").read()

# CORAL NOTES
# 32 scalar registers, 32-bits?

#def fix(y):
#  return bytes([int("0x"+x, 16) for x in y.split()])
#op = fix("00 08 00 00 00 00 C0 1B  00 AA AA AA AA 00 00 00")
#print(op)

ins = BitStruct(
  "unk_3" / BitsInteger(26),
  "imm_scalar" / BitsInteger(32),
  "s_y" / BitsInteger(5),
  "s_x" / BitsInteger(5),
  "s_op" / BitsInteger(6),
  "imm_size" / BitsInteger(32),
  "prefix" / BitsInteger(22),
)
# TODO: can assert that it's 128?
assert ins.sizeof() == 16

def dec(my_dat, off=-1):
  my_dat = my_dat[:0x10]
  #hexdump(my_dat)
  dd = ins.parse(my_dat[::-1])
  prt = []
  for k,v in list(dd.items())[::-1]:
    if k == "_io": continue
    prt.append("%12s:%8x" % (k,v))
  print(f"{off:4X}" + ','.join(prt))

for i in range(0, len(dat), 0x10):
  dec(dat[i:i+0x10], i)

#exit(0)
#dec(dat[0x180:])

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

ADDI = 0x21   # s_x <- s_y + imm_scalar
SUBI = 0x22   # s_x <- s_y - imm_scalar
ANDI = 0x23   # s_x <- s_y & imm_scalar
ORRI = 0x24   # s_x <- s_y | imm_scalar
XORI = 0x25   # s_x <- s_y ^ imm_scalar

MOVI = 0x2f   # s_x <- imm_scalar

print("my program")
prog = []
prog += mins(prefix=0x800, s_op=MOVI, s_x=0xc, imm_scalar=0xa3371337)
prog += mins(prefix=0x800, s_op=SUBI, s_x=0, s_y=0xc, imm_scalar=0xF000FFF0)
prog += mins(prefix=0x10840) # halt

# add start at the end
prog =  mins(prefix=0xf80, imm_size=len(prog)*0x10) + prog  # start
prog += mins(prefix=0xfc0, imm_size=0x10)  # end
prog = b''.join(prog)
hexdump(prog)

with open("programs/custom.coral", "wb") as f:
  f.write(prog)