#!/usr/bin/env python3
import struct
import ctypes
from hexdump import hexdump
from construct import BitStruct, BitsInteger
from collections import defaultdict

dat = open("programs/div2_8.coral", "rb").read()

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
  "s_reg" / BitsInteger(5),
  "imm_size" / BitsInteger(27),
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

mdat = []
for i in range(0, len(dat), 0x10):
  dec(dat[i:i+0x10], i)
  mdat.append(dat[i:i+0x10])

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

# 0x20 does nothing?

# drop the 0x20 and use reg[imm_scalar] instead
ADD = 0x1     # s_x <- s_y + s[imm_scalar]
UNK = 2

# math
ADDI = 0x21   # s_x <- s_y + imm_scalar
SUBI = 0x22   # s_x <- s_y - imm_scalar
ANDI = 0x23   # s_x <- s_y & imm_scalar
ORRI = 0x24   # s_x <- s_y | imm_scalar
XORI = 0x25   # s_x <- s_y ^ imm_scalar
SHLI = 0x26   # s_x <- s_y << imm_scalar
SHRI = 0x27   # s_x <- s_y >> imm_scalar
ASRI = 0x28   # s_x <- s_y >> imm_scalar (arithmetic)

# compare (the lt and gt are only somewhat right)
EQI  = 0x29
NEQI = 0x2A   # pred(s_x) <- s_y != imm_scalar
GTI  = 0x2B   # pred(s_x) <- s_y > imm_scalar (signed)
ULTI = 0x2C   # pred(s_x) <- s_y < imm_scalar (signed)
GEQI = 0x2D   # pred(s_x) <- s_y >= imm_scalar
GESI = 0x2E   # pred(s_x) <- s_y >= imm_scalar (unsigned)

# movement
MOVI = 0x2f   # s_x <- imm_scalar

print("my program")
prog = []
prog += mins(prefix=0x800, s_op=MOVI, s_x=0xb, imm_scalar=0xabab)
prog += mins(prefix=0x800, s_op=MOVI, s_x=0xc, imm_scalar=0x13371337)
prog += mins(prefix=0x800, s_op=UNK, s_x=0, s_y=0xc, imm_scalar=0xb)
#prog += mins(prefix=0x800, s_op=UNK, s_x=1, s_y=0xc, imm_scalar=0x13371336)
#prog += mins(prefix=0x800, s_op=UNK, s_x=2, s_y=0xc, imm_scalar=0x13371337)
#prog += mins(prefix=0x800, s_op=UNK, s_x=3, s_y=0xc, imm_scalar=0x13371338)
#prog += mins(prefix=0x800, s_op=UNK, s_x=4, s_y=0xc, imm_scalar=0xa3371338)

#prog = mdat[0x7b:0xad]
#prog = mdat[0xaa:0xad]
#prog += mdat[0x8a:0x8f]

# send status response (imm_scalar can be changed within a small range)
prog += mins(prefix=0x800, s_reg=8, imm_size=0x9400)
prog += mins(prefix=0x800, s_op=MOVI, s_x=0x15, imm_scalar=5)
prog += mins(prefix=0x800, s_reg=0x15, imm_size=0xd400)
prog += mins(prefix=0x800, imm_size=0x1800)

# add start at the end
prog =  mins(prefix=0xf80, imm_size=(len(prog)+1)*0x10) + prog  # start
prog += mins(prefix=0x10840) # halt
prog += mins(prefix=0xfc0, imm_size=0x10)  # end
prog = b''.join(prog)
hexdump(prog)

#prog = dat

with open("programs/custom.coral", "wb") as f:
  f.write(prog)