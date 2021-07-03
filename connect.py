#!/usr/bin/env python3
import time
import struct
from hexdump import hexdump
import binascii
import usb.core
import usb.util
#libusb_control_transfer(0x80, 6, reg:0x   100, 0x16bb36bae, wLength: 18) : 12 01 10 03 00 00 00 09 d1 18 02 93 00 01 00 00 00 01   
setup = """
libusb_control_transfer(0xc0, 1, reg:0x 1a30c, 0x16f4f2c0c, wLength: 4) : 01 00 6a b7
libusb_control_transfer(0x40, 1, reg:0x 1a30c, 0x16f4f2d3c, wLength: 4) : 59 00 0f 00
libusb_control_transfer(0xc0, 1, reg:0x 1a314, 0x16f4f2c0c, wLength: 4) : 59 00 0f 00
libusb_control_transfer(0xc0, 1, reg:0x 1a318, 0x16f4f2bfc, wLength: 4) : 00 00 00 00
libusb_control_transfer(0xc0, 1, reg:0x 1a318, 0x16f4f2bcc, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a318, 0x16f4f2cfc, wLength: 4) : 5c 02 85 50
libusb_control_transfer(0xc0, 1, reg:0x 1a318, 0x16f4f2bcc, wLength: 4) : 5c 02 c5 50
libusb_control_transfer(0xc0, 0, reg:0x 44018, 0x16f4f2b48, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4a000, 0x16f4f2cf8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 48788, 0x16f4f2cf8, wLength: 8) : 7f 00 00 00 00 00 00 00
libusb_control_transfer(0xc0, 0, reg:0x 48788, 0x16f4f2b48, wLength: 8) : 00 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 40020, 0x16f4f2cf8, wLength: 8) : 02 1e 00 00 00 00 00 00
libusb_control_transfer(0xc0, 1, reg:0x 1a314, 0x16f4f2c1c, wLength: 4) : 00 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a314, 0x16f4f2d4c, wLength: 4) : 00 00 15 00
libusb_control_transfer(0xc0, 1, reg:0x 1a000, 0x16f4f2adc, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c148, 0x16f4f2c08, wLength: 8) : f0 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c160, 0x16f4f2c08, wLength: 8) : 00 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 4c058, 0x16f4f2c08, wLength: 8) : 80 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 44018, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 44158, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 44198, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 441d8, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 44218, 0x16f4f2ce8, wLength: 8) : 01 00 00 00 00 00 00 00
libusb_control_transfer(0x40, 0, reg:0x 48788, 0x16f4f2ce8, wLength: 8) : 7f 00 00 00 00 00 00 00
libusb_control_transfer(0xc0, 0, reg:0x 48788, 0x16f4f2b38, wLength: 8) : 08 00 00 00 00 00 00 00
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
libusb_control_transfer(0xc0, 1, reg:0x 1a0d4, 0x16f4f2bfc, wLength: 4) : 00 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a0d4, 0x16f4f2d2c, wLength: 4) : 01 00 00 80
libusb_control_transfer(0xc0, 1, reg:0x 1a704, 0x16f4f2bec, wLength: 4) : 00 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a704, 0x16f4f2d1c, wLength: 4) : 7f 00 00 00
libusb_control_transfer(0xc0, 1, reg:0x 1a33c, 0x16f4f2bec, wLength: 4) : 7f 00 70 00
libusb_control_transfer(0x40, 1, reg:0x 1a33c, 0x16f4f2d1c, wLength: 4) : 3f 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a500, 0x16f4f2d4c, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a600, 0x16f4f2d4c, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a558, 0x16f4f2d4c, wLength: 4) : 03 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a658, 0x16f4f2d4c, wLength: 4) : 03 00 00 00
libusb_control_transfer(0xc0, 1, reg:0x 1a0d8, 0x16f4f2bfc, wLength: 4) : 01 00 00 00
libusb_control_transfer(0x40, 1, reg:0x 1a0d8, 0x16f4f2d2c, wLength: 4) : 00 00 00 80
"""

et = open("/Users/taylor/fun/edgetpu/libcoral/test_data/inception_v4_299_quant_edgetpu.tflite", "rb").read()
def csend(dev, off, ll, num):
  needle = binascii.unhexlify(off.replace(" ", ""))
  off = et.find(needle)
  off2 = et.find(needle, off+1)
  assert(off2 == -1)
  print("sending 0x%x with length 0x%x num %d" % (off, ll, num))
  header = struct.pack("II", ll, num)
  hexdump(header)
  dev.write(1, header)
  while ll > 0x100000:
    bdat = et[off:off+0x100000]
    #hexdump(bdat[0:0x10])
    dev.write(1, bdat)
    off += 0x100000
    ll -= 0x100000
  dev.write(1, et[off:off+ll])

dev = usb.core.find(idVendor=0x18d1, idProduct=0x9302)
usb.util.claim_interface(dev, 0)
dev.set_configuration(1)

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
  print(hex(reqType), bReq, hex(regnum), data, ret)

csend(dev, "80 0f 00 ac 05 00 00 00 00 00 00 00 00 00 00 00 80 f6 ff 0f 00 f8 ff 7f 00 80 ff 01 00 08 00 00", 0x16d0, 0)
csend(dev, "d8 cb ff ff db c8 ff ff 14 0e 00 00 19 0e 00 00 65 0b 00 00 b8 39 00 00 d4 d9 ff ff ac cc ff ff", 0x607500, 2)
#csend(dev, et.find(binascii.unhexlify("80 0f 00 00 ff 00 00 00 00 00 00 00 00 00 00 00 80 f6 ff 0f 00 f0 ff 7f 00 80 ff 01".replace(" ", ""))), 0x3fc20, 0)

#print(dev)
print("read")
dat = dev.read(0x82, 0x10, timeout=6000)
hexdump(dat)

dev.reset()

#print(dev)

