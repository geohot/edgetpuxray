#!/usr/bin/env python3
import struct
import ctypes
from hexdump import hexdump
from construct import BitStruct, BitsInteger
from collections import defaultdict
from colored import stylize, fg
altdat = []

dat = open("programs/div2.coral", "rb").read()
altdat = open("programs/relu.coral", "rb").read()
#dat = open("programs/inception_0.coral", "rb").read()
#altdat = open("programs/add1.coral", "rb").read()
#dat = open("programs/matmul_256.coral", "rb").read()
#dat = open("programs/div2_10_aarch64.coral", "rb").read()
#altdat = open("programs/div2_20_aarch64.coral", "rb").read()
#dat = open("programs/dense_1_8_mul.coral", "rb").read()

# https://patentimages.storage.googleapis.com/78/26/c0/f8767a76a0342e/US20190050717A1.pdf
# CORAL NOTES
# 32 scalar registers, 32-bits?
# 8 predicate registers

ins = BitStruct(
  "unk_3" / BitsInteger(18),
  "vs_reg_w" / BitsInteger(5), # confirmed as reg
  "v_op_2" / BitsInteger(3),

  # these 4 are correct
  "imm_scalar" / BitsInteger(32),
  "s_y" / BitsInteger(5),  # confirmed as reg
  "s_x" / BitsInteger(5),  # confirmed as reg
  "s_op" / BitsInteger(6),

  # unknown?
  "vs_reg" / BitsInteger(5),  # confirmed as reg
  "v_cmd" / BitsInteger(5),   # could be reg?
  "v_offset" / BitsInteger(8),
  # v_op and imm_size are fused with prefix = 0x7c
  "v_op" / BitsInteger(5),
  "imm_size" / BitsInteger(12),
  "vs_reg_v1" / BitsInteger(5),  # confirmed as reg

  # both of these seem gated on the preds
  "enable_vector" / BitsInteger(2),
  "enable_scalar" / BitsInteger(1),

  # this is probably the branch engine
  "branch" / BitsInteger(5),
  "unk_0" / BitsInteger(1),

  # these three are correct, not always :(
  "yes_pred" / BitsInteger(1),
  "pred_reg" / BitsInteger(3),
  "gate" / BitsInteger(1),  # run if *pred_reg == 0
)
# TODO: can assert that it's 128?
assert ins.sizeof() == 16

ops = ["NOP", "ADD", "SUB", "AND", "ORR", "XOR", "SHL", "SHR", "ASR", "EQ", "NEQ", "GT", "ULT", "GEQ", "GES", "MOV"]

def dec(my_dat, off=-1, cmp=None):
  my_dat = my_dat[:0x10]
  #hexdump(my_dat)
  dd = ins.parse(my_dat[::-1])
  if cmp:
    dd_alt = ins.parse(cmp[::-1])

  has_diff = True
  did_swap = False
  while has_diff:
    has_diff = False

    prt = []
    for k,v in list(dd.items())[::-1]:
      if k == "_io": continue
      if k not in ['gate', 'pred_reg', 'yes_pred', 'enable_vector', 'enable_scalar']:
        if cmp and dd_alt[k] != dd[k]:
          prt.append(stylize("%8s:%8x" % (k,v), fg('red') if did_swap else fg('green')))
          if not did_swap: has_diff = True
        else:
          prt.append("%8s:%8x" % (k,v))
    ff = ""
    if dd['enable_scalar']:
      ff += "S"
    if dd['enable_vector']:
      ff += "V"+str(dd['enable_vector'])
    pp = ""
    if dd['gate']:
      if not dd['yes_pred']:
        pp += "!"
      pp += str(dd['pred_reg'])

    print(f"{off:4X} {ff:3s}{pp:5s}", end="")
    more = ""
    if dd['v_op'] == 0xc:
      more = "USB ACT"
    elif dd['enable_scalar'] and dd['branch'] == 0:
      imm = f"0x{dd['imm_scalar']:X}" if dd['s_op'] & 0x20 else f"s{dd['imm_scalar']&0x1F}"
      more = f"{'C' if dd['s_op']&0xF in [9,10,11,12,13,14] else 's'}{dd['s_x']} <- s{dd['s_y']} {ops[dd['s_op']&0xF]} {imm}"
    print("%-30s" % more, f','.join(prt))

    if cmp:
      dd_alt, dd = dd, dd_alt
      did_swap = True


mdat = []
for i in range(0, len(dat), 0x10):
  dec(dat[i:i+0x10], i, altdat[i:i+0x10])
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

template = ins.parse(dat[0:0x10])
def mins(**kwargs):
  ret = defaultdict(lambda: 0)
  for k,v in kwargs.items():
    assert k in template
    ret[k] = v
  return [ins.build(ret)[::-1]]

# 0x20 does nothing?

# drop the 0x20 and use reg[imm_scalar] instead
ADD = 0x1     # s_x <- s_y + s[imm_scalar]
SUB = 0x2
EQ = 0x9
NEQ = 0xA

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

# 0x800 in the prefix mean imm_scalar should go on the bus

print("my program")
prog = []
#prog += mins(branch=0x20)
prog += mins(enable_scalar=0x1, s_op=MOVI, s_x=0, imm_scalar=0xabab)
prog += mins(v_op_2=1, vs_reg_w=6)  # set s6 = 0x7F800000
prog += mins(enable_vector=1, vs_reg_v1=0xc)
prog += mins(enable_vector=1, vs_reg_v1=0xd, v_op=3, vs_reg=0x1d, imm_size=0xfff, unk_3=0x3ffa0)

#prog += mins(vs_reg_v1=0x14, imm_size=0xfff, v_op=3, vs_reg=0x1d, s_op=0x3f, s_x=0x1f, s_y=1, imm_scalar=0x1fffd000, unk_3=0x3ffa0)
#prog += mins(vs_reg_v1=3, imm_size=6, v_offset=0xfe, v_cmd=0x1d, vs_reg=0xf, s_op=0x1f, imm_scalar=0x21bf80)




#prog += mins(enable_scalar=0x1, s_op=MOVI, s_x=0xb, imm_scalar=0xabab, vs_reg=0, v_op_2=7, vs_reg_w=5)
#prog += mins(enable_scalar=0x1, s_op=MOVI, s_x=0, imm_scalar=0xabab)

#for i in range(8): prog += mins(v_op_2=i, vs_reg_w=0x10+i, imm_scalar=0x20000000, unk_3=0x20002)

#prog += mins(enable_scalar=1, enable_vector=1,
#  vs_reg_v1=0x12, imm_size=0xff, v_op=1, v_offset=1, vs_reg=1,
#  s_op=ADDI, s_x=4, s_y=1, imm_scalar=0xeeff,
#  unk_3=0x3ffff)
#prog += mins(enable_vector=1, vs_reg_v1=0x13, unk_3=0x3ffff)
#prog += mins(enable_vector=1, vs_reg_v1=0x14)
#prog += mins(enable_scalar=0, vs_reg_v1=0x13, enable_vector=2, s_op=MOVI, s_x=0xb, imm_scalar=0xabab, vs_reg=0, v_op_2=0, vs_reg_w=0)
#prog += mins(prefix=0x10, s_op=MOVI, s_x=0xc, imm_scalar=0x13371337)
#prog += mins(prefix=0x10, s_op=SUB, s_x=2, s_y=0xc, imm_scalar=0xb)

#for i in range(4, 8): prog += mins(prefix=0x800, s_op=EQ, s_x=i, s_y=0, imm_scalar=0)
"""
prog += mins(prefix=0x40, s_op=EQ, s_x=2, s_y=0, imm_scalar=0)
prog += mins(prefix=0x40, s_op=EQ, s_x=4, s_y=0, imm_scalar=0)
prog += mins(prefix=0x40, s_op=EQ, s_x=5, s_y=0, imm_scalar=0)
prog += mins(prefix=0x40, s_op=EQ, s_x=7, s_y=0, imm_scalar=0)
"""

"""
prog += mins(prefix=0x20, run_flag=0, pred_reg=1, s_op=MOVI, s_x=0x10, imm_scalar=0xcafebabe)
prog += mins(prefix=0x20, run_flag=1, pred_reg=1, s_op=MOVI, s_x=0x11, imm_scalar=0xcafebabe)  # run if preg_reg == 0
prog += mins(prefix=0x20, run_flag=2, pred_reg=1, s_op=MOVI, s_x=0x12, imm_scalar=0xcafebabe)
prog += mins(prefix=0x20, run_flag=3, pred_reg=1, s_op=MOVI, s_x=0x13, imm_scalar=0xcafebabe)  # run if pred_reg == 1
prog += mins(prefix=0x20, run_flag=0, pred_reg=2, s_op=MOVI, s_x=0x14, imm_scalar=0xcafebabe)
prog += mins(prefix=0x20, run_flag=1, pred_reg=2, s_op=MOVI, s_x=0x15, imm_scalar=0xcafebabe)  # run if preg_reg == 1
prog += mins(prefix=0x20, run_flag=2, pred_reg=2, s_op=MOVI, s_x=0x16, imm_scalar=0xcafebabe)
prog += mins(prefix=0x20, run_flag=3, pred_reg=2, s_op=MOVI, s_x=0x17, imm_scalar=0xcafebabe)  # run if preg_reg == 0
"""

"""
prog += mins(prefix=0x40, gate=1, pred_reg=0, yes_pred=1, s_op=MOVI, s_x=0x10, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=1, yes_pred=1, s_op=MOVI, s_x=0x11, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=2, yes_pred=1, s_op=MOVI, s_x=0x12, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=3, yes_pred=1, s_op=MOVI, s_x=0x13, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=4, yes_pred=0, s_op=MOVI, s_x=0x14, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=5, yes_pred=0, s_op=MOVI, s_x=0x15, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=6, yes_pred=0, s_op=MOVI, s_x=0x16, imm_scalar=0xcafebabe)
prog += mins(prefix=0x40, gate=1, pred_reg=7, yes_pred=0, s_op=MOVI, s_x=0x17, imm_scalar=0xcafebabe)
"""

#prog += mins(prefix=0x800, s_op=UNK, s_x=1, s_y=0xc, imm_scalar=0x13371336)
#prog += mins(prefix=0x800, s_op=UNK, s_x=2, s_y=0xc, imm_scalar=0x13371337)
#prog += mins(prefix=0x800, s_op=UNK, s_x=3, s_y=0xc, imm_scalar=0x13371338)
#prog += mins(prefix=0x800, s_op=UNK, s_x=4, s_y=0xc, imm_scalar=0xa3371338)

#prog = mdat[0xaa:0xad]
#prog += mdat[0x8a:0x8f]

#prog += mins(prefix=0x10, s_op=MOVI, s_x=6, imm_scalar=0xccdd3333)
#prog += mins(prefix=0x10, s_op=MOVI, s_x=7, imm_scalar=0x13371337)
#prog += mins(prefix=0x10, s_op=MOVI, s_x=8, imm_scalar=0xaabbccdd)

# without 0x800 these instructions don't work
#prog += mins(prefix=0x10, vs_reg=6, v_op=5, imm_offset=0)
#prog += mins(prefix=0x10, vs_reg=7, v_op=5, imm_offset=1)
#prog += mins(prefix=0x10, vs_reg=8, v_op=5, imm_offset=2)


#prog = mdat[4:0x1a]

# send "output tensor" (EP 1)
"""
# very confusing
prog += mins(prefix=0x14c0, vs_reg=2, s_y=0x18, imm_scalar=0xe000100) #, unk_3=0x3fffe00)
prog += mins(prefix=0x390000, imm_size=0x7ff, vs_reg=0x19, s_op=0x3f, s_x=0x1f, s_y=1, imm_scalar=0x1fff9000) #, unk_3=0x3ffe000)
prog += mins(prefix=0x10000f, imm_scalar=0x840f000)
prog += mins() #prog += mins(unk_3=0x28)
prog += mins(imm_size=0x600) #, imm_offset=0x1f98, vs_reg=0x1f, s_op=0x3f, imm_scalar=0x60)
prog += mins()
prog += mins()  # extra NOP lets you move into scalar 8 early

# TODO: wtf, why can't I move into scalar 8 early
prog += mins(prefix=0x800, s_op=MOVI, s_x=6, imm_scalar=0)
prog += mins(prefix=0x800, s_op=MOVI, s_x=7, imm_scalar=0)
prog += mins(prefix=0x800, s_op=MOVI, s_x=8, imm_scalar=0x18)  # output length (8 for 8)
prog += mins(prefix=0x800, s_op=MOVI, s_x=9, imm_scalar=3)
prog += mins(prefix=0x800, vs_reg=6, imm_size=0x1400)
prog += mins(prefix=0x800, vs_reg=7, imm_size=0x1400, imm_offset=1)
prog += mins(prefix=0x800, vs_reg=8, imm_size=0x1400, imm_offset=2)
prog += mins(prefix=0x800, vs_reg=9, imm_size=0x1400, imm_offset=3)
prog += mins(prefix=0x800, imm_size=0x1800)

# bottom part
# this has to length for output length
prog += mins(prefix=0x9c0, imm_offset=0x180)   #prog += mins(prefix=0x9c0, imm_size=0x20) (for 8)
prog += mins(imm_scalar=0x7f000000)   #prog += mins(imm_offset=0x600, imm_scalar=0x7f000000)
prog += mins(prefix=0x1400, imm_offset=0x400, vs_reg=2, s_x=0x18, s_y=3, imm_scalar=0x108)
prog += mins()   #prog += mins(imm_scalar=0x51000)
prog += mins()   #prog += mins(imm_scalar=0xa2a600, unk_3=0x1000100)
prog += mins(prefix=0xad, imm_size=2, imm_offset=8, imm_scalar=0x20000000)
"""

# min USB status output
prog += mins(enable_scalar=0x1, s_op=MOVI, s_x=0x1b, imm_scalar=4)  # this one has a small range
prog += mins(enable_scalar=0x1, vs_reg=0x1b, v_op=0xa, v_offset=3)
prog += mins(enable_scalar=0x1, v_op=0xc)

# add start at the end
prog =  mins(branch=0x3c>>1, enable_scalar=1, imm_size=(len(prog)+5)*0x10*8) + prog  # start
prog += mins(branch=2>>1, enable_scalar=1)    # halt
# 4 nops
prog += mins(enable_scalar=1)
prog += mins(enable_scalar=1)
prog += mins(enable_scalar=1)
prog += mins(enable_scalar=1)
prog += mins(branch=0x3e>>1, enable_scalar=1, imm_size=0x10*8)  # end
prog = b''.join(prog)
hexdump(prog)

for i in range(0, len(prog), 0x10):
  dec(prog[i:i+0x10], i)

#prog = dat

with open("programs/custom.coral", "wb") as f:
  f.write(prog)