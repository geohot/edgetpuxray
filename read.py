#!/usr/bin/env python3
from PIL import Image
import sys

im = Image.open(sys.argv[1])
im = im.resize((299, 299))
pixels = list(im.getdata())
out = []
for p in pixels:
  out += p

with open(sys.argv[1].split(".")[0]+".dat", "wb") as f:
  f.write(bytes(out))

