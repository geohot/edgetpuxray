#!/usr/bin/env python3
import time
import usb.core
import usb.util
from hexdump import hexdump
import struct
import binascii

def q(x):
  return struct.pack("Q", x)

# may download firmware
def open_device():
  dev = usb.core.find(idVendor=0x18d1, idProduct=0x9302)
  if dev is None:
    # download firmware
    dev = usb.core.find(idVendor=0x1a6e, idProduct=0x089a)
    if dev is None:
      raise Exception("U NEED TO BUY GOOGLE CORAL NO FREE BANANA FOR U")
    print("doing download firmware bro")
    fw = open("apex_latest_single_ep.bin", "rb").read()
    cnt = 0
    for i in range(0, len(fw), 0x100):
      dev.ctrl_transfer(0x21, 1, cnt, 0, fw[i:i+0x100])
      ret = dev.ctrl_transfer(0xa1, 3, 0, 0, 6)
      hexdump(ret)
      cnt += 1
    dev.ctrl_transfer(0x21, 1, cnt, 0, "")
    ret = dev.ctrl_transfer(0xa1, 3, 0, 0, 6)
    hexdump(ret)

    for i in range(0, 0x81):
      ret = dev.ctrl_transfer(0xa1, 2, i, 0, 0x100)
    try: 
      dev.reset()
    except usb.core.USBError:
      print("okay exception")
    print("downloaded, napping quick bro")
    time.sleep(3)

    dev = usb.core.find(idVendor=0x18d1, idProduct=0x9302)
  dev.reset()
  time.sleep(0.6)
  usb.util.claim_interface(dev, 0)
  dev.set_configuration(1)
  return dev

regs = [x.strip().split(' // NOLINT: ') for x in open("beagle_csr_offsets.h").read().split("\n") if ' // NOLINT: ' in x]
regs = {int(x.strip(' ,'),16):y for x,y in regs}
iregs = {y:x for x,y in regs.items()}

def llsend(dev, dat, num):
  ll = len(dat)
  off = 0
  header = struct.pack("II", ll, num)
  hexdump(header)
  dev.write(1, header)
  #if num == 0: hexdump(dat[:0x100])
  while ll > 0x100000:
    bdat = dat[off:off+0x100000]
    #hexdump(bdat[0:0x10])
    dev.write(1, bdat)
    off += 0x100000
    ll -= 0x100000
  dev.write(1, dat[off:off+ll])

def write_register(dev, name, data):
  regnum = iregs[name]
  bReq = int(regnum>>16 == 1)
  print(f"writing {name:30s} {bReq} 0x{regnum:X} with {len(data)} bytes {data}")
  ret = dev.ctrl_transfer(0x40, bReq, regnum & 0xFFFF, regnum >> 16, data)

def read_register(dev, name, llen, offset=0, debug=True):
  regnum = iregs[name] + offset
  bReq = int(regnum>>16 == 1)
  ret = dev.ctrl_transfer(0xc0, bReq, regnum & 0xFFFF, regnum >> 16, llen)
  nret = struct.unpack("Q" if llen == 8 else "I", ret)[0]
  if debug:
    print(f"reading {name:30s} {bReq} 0x{regnum:X} -> 0x{nret:X}")
  return ret

def read_pc(dev):
  pc = read_register(dev, 'currentPc', 8)
  pc = struct.unpack("Q", pc)[0] * 0x10
  print(f"PC: 0x{pc:X}")

if __name__ == "__main__":
  #for k,v in regs.items(): print(f"{k:8X} : {v}")
  dev = open_device()

  read_register(dev, 'efuse_00', 4)

  write_register(dev, 'scu_ctrl_0', b'\x59\x00\x0f\x00')
  write_register(dev, 'scu_ctrl_3', b'\x5c\x02\x85\x50')
  write_register(dev, 'idleRegister', b'\x01\x00\x00\x00\x00\x00\x00\x00')
  write_register(dev, 'tileconfig0', b'\x7f\x00\x00\x00\x00\x00\x00\x00')
  write_register(dev, 'deepSleep', b'\x02\x1e\x00\x00\x00\x00\x00\x00')
  write_register(dev, 'scu_ctrl_2', b'\x00\x00\x15\x00')
  write_register(dev, 'descr_ep', b'\xf0\x00\x00\x00\x00\x00\x00\x00')
  write_register(dev, 'multi_bo_ep', b'\x00\x00\x00\x00\x00\x00\x00\x00')
  write_register(dev, 'outfeed_chunk_length', b'\x80\x00\x00\x00\x00\x00\x00\x00')
  write_register(dev, 'avDataPopRunControl', q(1))
  write_register(dev, 'parameterPopRunControl', q(1))
  write_register(dev, 'infeedRunControl', q(1))
  write_register(dev, 'outfeedRunControl', q(1))
  write_register(dev, 'tileconfig0', q(0x7f))
  write_register(dev, 'opRunControl', q(1))
  write_register(dev, 'narrowToWideRunControl', q(1))
  write_register(dev, 'wideToNarrowRunControl', q(1))
  write_register(dev, 'meshBus0RunControl', q(1))
  write_register(dev, 'meshBus1RunControl', q(1))
  write_register(dev, 'meshBus2RunControl', q(1))
  write_register(dev, 'meshBus3RunControl', q(1))
  write_register(dev, 'ringBusConsumer0RunControl', q(1))
  write_register(dev, 'ringBusConsumer1RunControl', q(1))
  write_register(dev, 'ringBusProducerRunControl', q(1))
  write_register(dev, 'fatal_err_int_control', q(1))
  write_register(dev, 'top_level_int_0_control', q(1))
  write_register(dev, 'top_level_int_1_control', q(1))
  write_register(dev, 'top_level_int_2_control', q(1))
  write_register(dev, 'top_level_int_3_control', q(1))
  write_register(dev, 'omc0_d4', b'\x01\x00\x00\x80')
  write_register(dev, 'rambist_ctrl_1', b'\x7f\x00\x00\x00')
  write_register(dev, 'scu_ctr_7', b'\x3f\x00\x00\x00')
  write_register(dev, 'slv_abm_en', b'\x01\x00\x00\x00')
  write_register(dev, 'mst_abm_en', b'\x01\x00\x00\x00')
  write_register(dev, 'slv_err_resp_isr_mask', b'\x03\x00\x00\x00')
  write_register(dev, 'mst_err_resp_isr_mask', b'\x03\x00\x00\x00')
  write_register(dev, 'omc0_d8', b'\x00\x00\x00\x80')
  
  read_register(dev, 'currentPc', 8)

  # single step mode
  #write_register(dev, 0, 'scalarCoreRunControl', b'\x03\x00\x00\x00\x00\x00\x00\x00')

  # run program
  prog = open("programs/custom.coral", "rb").read()
  #prog = open("programs/div2.coral", "rb").read()
  #prog = open("programs/mul2_add10.coral", "rb").read()
  def fix(y):
    return bytes([int("0x"+x, 16) for x in y.split()])

  END = fix("40 08 01 00 00 00 00 00  00 00 00 00 00 00 00 00")
  PAD = fix("C0 0F 00 04 00 00 00 00  00 00 00 00 00 00 00 00")
  NOP = fix("00 08 00 00 00 00 00 00  00 00 00 00 00 00 00 00")
  #END = b"\xff" * 0x10

  # 0x10 : PC = 8
  # 0x20 : PC = 17

  # mask 0x10 instruction
  #offset = 0x30
  #prog = prog[:offset] + END + prog[offset+0x10:]

  #prog = END + prog[0x10:]

  #prog = prog[0:0xad0] + END + PAD*5
  #print(hex(len(prog)))

  #prog = prog[:0x40] + prog[0x50:] + END
  #prog = prog[:0x40] + prog[0x50:] + END

  """
  prog = prog[0:4] + b"\x00" + prog[5:]

  prog = prog[0:0x10] + NOP*3 + prog[0x40:]
  prog = prog[0:0x49] + b"\xaa\xaa\xaa\xaa\x00" + prog[0x4e:]
  prog = prog[0:0x79] + b"\xbb\xbb\xbb\xbb\x00" + prog[0x7e:]
  prog = prog[0:0x80] + END + PAD * 0xb0 #+ prog[0x90:]
  hexdump(prog[0:0x100])
  """

  # skip 0x420 instruction
  #prog = prog[:0x420] + b"\x00"*0x10 + preg[0x430:]

  # download the program
  llsend(dev, prog, 0)

  # set a breakpoint
  #write_register(dev, 'scalarCoreBreakPoint', q((0x130//0x10) << 1 | 1))
  #read_register(dev, 'instruction_queue_int_status', 8)
  #write_register(dev, 'currentPc', q(21))
  #read_register(dev, 'currentPc', 8)


  # run it
  read_register(dev, 'scalarCoreRunStatus', 8)
  write_register(dev, 'scalarCoreRunControl', b'\x01\x00\x00\x00\x00\x00\x00\x00')
  read_register(dev, 'scalarCoreRunStatus', 8)
  #read_register(dev, 'scMemoryAccess', 8)
  #read_register(dev, 'scMemoryData', 8)

  # download weights
  read_pc(dev)
  print("download weights")
  #dat = dev.read(0x82, 0x400, timeout=6000)
  #hexdump(dat)
  llsend(dev, b"\xaa"*0x80, 2)

  # unset breakpoint and run
  #write_register(dev, 'scalarCoreBreakPoint', q(0))
  #write_register(dev, 'scalarCoreRunControl', b'\x05\x00\x00\x00\x00\x00\x00\x00')
  #read_register(dev, 'instruction_queue_int_status', 8)


  # program gets to pc:66 waiting for data
  #write_register(dev, 'scalarCoreRunControl', b'\x00\x00\x00\x00\x00\x00\x00\x00')
  read_pc(dev)
  #write_register(dev, 'scalarCoreRunControl', b'\x01\x00\x00\x00\x00\x00\x00\x00')
  llsend(dev, b"\xc0\x80\x40\x20\xc0\x80\x04\x08"*4, 1)
  read_pc(dev)

  # halt the core and dump the registers
  write_register(dev, 'scalarCoreRunControl', b'\x02\x00\x00\x00\x00\x00\x00\x00')
  read_register(dev, 'scalarCoreRunStatus', 8)
  for i in range(0, 0x100, 8):
    read_register(dev, 'scalarRegisterFile', 8, offset=i)
  for i in range(0, 0x40, 8):
    read_register(dev, 'predicateRegisterFile', 8, offset=i)

  print("getting status response")
  dat = dev.read(0x82, 0x400, timeout=6000)
  hexdump(dat)
  read_register(dev, 'currentPc', 8)

  """
  print("getting output tensor")
  dat = dev.read(0x81, 0x400, timeout=6000)
  hexdump(dat)
  read_register(dev, 'currentPc', 8)
  read_register(dev, 'scalarCoreRunStatus', 8)
  """
