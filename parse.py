#!/usr/bin/env python3
import numpy as np
import tensorflow as tf

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="inception_v4_299_quant_edgetpu.tflite")

print(dir(interpreter))

#print(interpreter.get_tensor_details())
for x in interpreter._get_ops_details():
  print(x)

ri = interpreter._interpreter
print(ri)

print(ri.NumNodes(), ri.NodeName(0))

# RuntimeError: Encountered unresolved custom op: edgetpu-custom-op.
#interpreter.allocate_tensors()

"""
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(input_details, output_details)

input_shape = input_details[0]['shape']
input_data = np.array(np.random.random_sample(input_shape), dtype=np.uint8)
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
"""
