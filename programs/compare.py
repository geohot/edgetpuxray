#!/usr/bin/env python3
mul2 = open("relu_2.coral", "rb").read()
relu = open("relu_4.coral", "rb").read()
from termcolor import colored

assert len(mul2) == len(relu)

app = []
for i in range(len(mul2)):
  if i%8 == 0 and i != 0:
    app.append(" ")
  if i%0x10 == 0:
    if i != 0:
      app.append("\n")
    app.append("%8X : " % i)
  dat = "%02X" % mul2[i]
  dat2 = "%02X" % relu[i]
  if mul2[i] != relu[i]:
    app.append(colored(dat, 'red')+' ')
  else:
    app.append(dat+' ')

print(''.join(app))
