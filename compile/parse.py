#!/usr/bin/env python3
import numpy as np
import pprint
from hexdump import hexdump

# from https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/tools/visualize.py
from tensorflow.lite.python import schema_py_generated as schema_fb

def FlatbufferToDict(fb):
  if isinstance(fb, int) or isinstance(fb, float) or isinstance(fb, str):
    return fb
  elif isinstance(fb, np.ndarray):
    return fb
  elif isinstance(fb, bytes):
    return fb
  elif hasattr(fb, "__len__"):
    return [FlatbufferToDict(entry) for entry in fb]
  else: # hasattr(fb, "__dict__"):
    result = {}
    for attribute_name in dir(fb):
      attribute = fb.__getattribute__(attribute_name)
      if not callable(attribute) and attribute_name[0] != "_":
        result[attribute_name] = FlatbufferToDict(attribute)
    return result
  #else:
  #  return fb

#buffer_data = open("model.tflite", "rb").read()
buffer_data = open("model_edgetpu.tflite", "rb").read()
#buffer_data = open("../inception_v4_299_quant_edgetpu.tflite", "rb").read()

model_obj = schema_fb.Model.GetRootAsModel(buffer_data, 0)
model = schema_fb.ModelT.InitFromObj(model_obj)
fb = FlatbufferToDict(model)
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(fb)

op = fb['subgraphs'][0]['operators'][0]['customOptions']
print(len(op))
hexdump(op[0:0x20])
offset = bytes(op).find(b"DWN1") - 4
print("got offset", offset)

import flatbuffers
idd = flatbuffers.util.GetBufferIdentifier(op, offset, False)
print(bytes(idd))

# flatc -p executable.fbs 
from platforms.darwinn.Package import Package
from platforms.darwinn.MultiExecutable import MultiExecutable
from platforms.darwinn.Executable import Executable
exc = Package.GetRootAs(op, offset)

for x in dir(exc):
  if x[0] != "_":
    print(x)

print(exc.MultiChipPackageLength(), exc.SerializedMultiExecutableLength(), exc.SignatureLength())
print(exc.SerializedMultiExecutableAsNumpy())

dat = MultiExecutable.GetRootAs(exc.SerializedMultiExecutableAsNumpy())
print(dat)

for x in dir(dat):
  if x[0] != "_":
    print(x)

def print_field_offset(x):
  return (x.Meta().Desc(), x.Meta().Batch(), x.Meta().Name().decode('utf-8'), x.OffsetBit())

for i in range(dat.SerializedExecutablesLength()):
  print(i)
  se = Executable.GetRootAs(dat.SerializedExecutables(i))
  print(se.InstructionBitstreamsLength(), se.SerializedModelLength(), "parameters length", hex(se.ParametersLength()))
  for j in range(se.InstructionBitstreamsLength()):
    see = se.InstructionBitstreams(j)
    #print(dir(see))
    print(hex(see.BitstreamLength()), see.BitstreamLength(), [print_field_offset(see.FieldOffsets(i)) for i in range(see.FieldOffsetsLength())])
    hexdump(see.BitstreamAsNumpy()[0:0x20])
    fn = f"/tmp/prog_{i}_{j}"
    with open(fn, "wb") as f:
      f.write(see.BitstreamAsNumpy())
      print(f"writing {fn}")
