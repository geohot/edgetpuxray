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

setup = """
libusb_control_transfer(0x40, 0, reg:0x 44158, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 44198, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 441d8, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 44218, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 48788, 0x16f4f2ce8, wLength: 8) : 7f 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 400c0, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40150, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40110, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40250, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40298, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 402e0, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40328, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40190, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 401d0, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40210, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c060, 0x16f4f2d88, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c070, 0x16f4f2d38, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c080, 0x16f4f2d38, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c090, 0x16f4f2d38, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c0a0, 0x16f4f2d38, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a0d4, 0x16f4f2d2c, wLength: 4) : 01 00 00 80
libusb_control_transfer(0x40, 1, reg:0x 1a704, 0x16f4f2d1c, wLength: 4) : 7f 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a33c, 0x16f4f2d1c, wLength: 4) : 3f 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a500, 0x16f4f2d4c, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a600, 0x16f4f2d4c, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a558, 0x16f4f2d4c, wLength: 4) : 03 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a658, 0x16f4f2d4c, wLength: 4) : 03 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a0d8, 0x16f4f2d2c, wLength: 4) : 00 00 00 80
"""

def write_register(dev, name, data):
  regnum = iregs[name]
  bReq = int(regnum>>16 == 1)
  print(f"writing {name:30s} {bReq} 0x{regnum:X} with {len(data)} bytes")
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
  

  # setup registers
  for s in setup.strip().split("\n"):
    reqType, bReq = s.split("(")[1].split(",")[0:2]
    reqType, bReq = int(reqType, 16), int(bReq)

    s = s.split("reg:0x ")[1]
    regnum = int("0x"+s.split(",")[0].strip(), 16)
    data = binascii.unhexlify(s.split(" : ")[1].replace(" ", ""))
    wVal = regnum & 0xFFFF
    wIndex = regnum >> 16
    if reqType == 0xC0:
      data = len(data)
    ret = dev.ctrl_transfer(reqType, bReq, wVal, wIndex, data)
    print(hex(reqType), bReq, hex(regnum), regs[regnum], data, ret)
  
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
