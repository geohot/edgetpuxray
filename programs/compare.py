#!/usr/bin/env python3
#A = open("mul2.coral", "rb").read()
#B = open("mul2_fake.coral", "rb").read()

import sys
A = open(sys.argv[1], "rb").read()
B = open(sys.argv[2], "rb").read()
#B = open("relu_sub_1.coral", "rb").read()
from termcolor import colored

special_bits = [(2, 0, '', 582), (2, 0, '', 710), (3, 0, '', 838), (3, 0, '', 966), (1, 0, 'x', 1862), (1, 0, 'x', 1990), (0, 0, 'Identity', 14534), (0, 0, 'Identity', 14662)]
special_bytes = [x[3]//8 for x in special_bits]

app = []
tmp = []
def add_tmp():
  global app, tmp
  app.append("|  ")
  app += tmp
  tmp = []
for i in range(max(len(A), len(B))):
  if i%8 == 0 and i != 0:
    app.append(" ")
    tmp.append(" ")
  if i%0x10 == 0:
    if i != 0:
      add_tmp()
      app.append("\n")
    app.append("%8X : " % i)
  dA = ("%02X" % A[i]) if i < len(A) else "--"
  dB = ("%02X" % B[i]) if i < len(B) else "--"
  if dA != dB:
    app.append(colored(dA, 'green')+' ')
    tmp.append(colored(dB, 'green')+' ')
  else:
    if i in special_bytes:
      app.append(colored(dA, 'blue')+' ')
      tmp.append(colored(dB, 'blue')+' ')
    else:
      app.append(dA+' ')
      tmp.append(dB+' ')
app.append(' ')
add_tmp()

print(''.join(app))
