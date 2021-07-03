#!/bin/bash -e
DEPS=/Users/taylor/fun/edgetpu/tflite_build/_deps
g++ --std=c++11 -I /Users/taylor/fun/edgetpu/tensorflow -I ../libedgetpu/tflite/public/ -I /Users/taylor/fun/edgetpu/tensorflow/tensorflow/lite -I /Users/taylor/fun/edgetpu/tensorflow/ -I /Users/taylor/fun/edgetpu/tflite_build/flatbuffers/include main.cc -L/Users/taylor/fun/edgetpu/libedgetpu/out/throttled/darwin_arm64 -ledgetpu.1.0 -Wl,-rpath /Users/taylor/fun/edgetpu/libedgetpu/out/throttled/darwin_arm64/ /Users/taylor/fun/edgetpu/tflite_build/libtensorflow-lite.a $DEPS/ruy-build/libruy.a $DEPS/xnnpack-build/libXNNPACK.a /Users/taylor/fun/edgetpu/tflite_build/pthreadpool/libpthreadpool.a /Users/taylor/fun/edgetpu/tflite_build/cpuinfo/libcpuinfo.a $DEPS/fft2d-build/libfft2d_fftsg.a $DEPS/fft2d-build/libfft2d_fftsg2d.a /Users/taylor/fun/edgetpu/tflite_build/clog/libclog.a $DEPS/farmhash-build/libfarmhash.a -flat_namespace -I/opt/homebrew/include/libusb-1.0
DYLD_FORCE_FLAT_NAMESPACE=1 ./a.out data/banana.dat

