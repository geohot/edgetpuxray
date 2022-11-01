#!/usr/bin/env python3
import numpy as np
import pprint
from hexdump import hexdump

# from https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/tools/visualize.py
from tensorflow.lite.python import schema_py_generated as schema_fb

def FlatbufferToDict(fb):
  if isinstance(fb, int) or isinstance(fb, float) or isinstance(fb, str):
    return fb
  elif hasattr(fb, "__dict__"):
    result = {}
    for attribute_name in dir(fb):
      attribute = fb.__getattribute__(attribute_name)
      if not callable(attribute) and attribute_name[0] != "_":
        result[attribute_name] = FlatbufferToDict(attribute)
    return result
  elif isinstance(fb, np.ndarray):
    return fb
  elif isinstance(fb, bytes):
    return fb
  elif hasattr(fb, "__len__"):
    return [FlatbufferToDict(entry) for entry in fb]
  else:
    return fb

buffer_data = open("compile/model_edgetpu.tflite", "rb").read()
#buffer_data = open("inception_v4_299_quant_edgetpu.tflite", "rb").read()

model_obj = schema_fb.Model.GetRootAsModel(buffer_data, 0)
model = schema_fb.ModelT.InitFromObj(model_obj)
fb = FlatbufferToDict(model)
pp = pprint.PrettyPrinter(indent=2)
pp.pprint(fb)

op = fb['subgraphs'][0]['operators'][0]['customOptions']
print(len(op))
hexdump(op[0:0x200])

# flatc -p executable.fbs 
"""
from platforms.darwinn.Executable import Executable
exc = Executable.GetRootAsExecutable(op, 0)
print(dir(exc))
print(exc.InputLayersLength())
"""
