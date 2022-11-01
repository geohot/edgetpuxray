#!/usr/bin/env python3
import numpy as np
import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import tensorflow as tf
# example from https://www.tensorflow.org/lite/convert

# Create a model using high-level tf.keras.* APIs
"""
model = tf.keras.models.Sequential([
    #tf.keras.layers.ReLU(input_shape=[1])
    tf.keras.layers.Rescaling(4, input_shape=[1])
    #tf.keras.layers.Dense(units=1, input_shape=[1], use_bias=False),
    #tf.keras.layers.Dense(units=16, activation='relu'),
    #tf.keras.layers.Dense(units=1)
])
"""
#model.compile(optimizer='sgd', loss='mean_squared_error') # compile the model
#model.fit(x=[-1, 0, 1], y=[-3, -1, 1], epochs=5) # train the model
# (to generate a SavedModel) tf.saved_model.save(model, "saved_model_keras_dir")

def representative_dataset():
  for i in range(256):
    #data = np.random.rand(1, 1)
    data = np.array(i)
    yield [data.astype(np.float32)]

# Convert the model.
root = tf.train.Checkpoint()
#root.f = tf.function(lambda g_input: tf.nn.relu(g_input))
root.f = tf.function(lambda g_input: g_input*2+10)
#root.f = tf.function(lambda x: tf.nn.relu(x)-1)
input_data = tf.constant(1., shape=[8])
to_save = root.f.get_concrete_function(input_data)
print(to_save)

#print(to_save(tf.ones(1)*2))
#exit(-1)

converter = tf.lite.TFLiteConverter.from_concrete_functions([to_save])
#converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset

converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8  # or tf.uint8
converter.inference_output_type = tf.uint8  # or tf.uint8
tflite_model = converter.convert()

# Save the model.
with open('model.tflite', 'wb') as f:
  f.write(tflite_model)

# Compile it
os.system("./docker.sh")
