#!/bin/bash -e
DEPS=$HOME/fun/edgetpu/tflite_build/_deps
g++ --std=c++11 -I $HOME/fun/edgetpu/tensorflow_src -I $HOME/fun/edgetpu/libedgetpu/tflite/public/ -I $HOME/fun/edgetpu/tensorflow/tensorflow/lite -I $HOME/fun/edgetpu/tensorflow/ -I $HOME/fun/edgetpu/tflite_build/flatbuffers/include main.cc -L$HOME/fun/edgetpu/libedgetpu/out/throttled/darwin_arm64 -ledgetpu.1.0 -Wl,-rpath $HOME/fun/edgetpu/libedgetpu/out/throttled/darwin_arm64/ $HOME/fun/edgetpu/tflite_build/libtensorflow-lite.a $DEPS/ruy-build/libruy.a $DEPS/xnnpack-build/libXNNPACK.a $HOME/fun/edgetpu/tflite_build/pthreadpool/libpthreadpool.a $HOME/fun/edgetpu/tflite_build/cpuinfo/libcpuinfo.a $DEPS/fft2d-build/libfft2d_fftsg.a $DEPS/fft2d-build/libfft2d_fftsg2d.a $HOME/fun/edgetpu/tflite_build/clog/libclog.a $DEPS/farmhash-build/libfarmhash.a -flat_namespace -I/opt/homebrew/include/libusb-1.0 -L/opt/homebrew/opt/libusb/lib/ -lusb-1.0
DYLD_FORCE_FLAT_NAMESPACE=1 ./a.out inception_v4_299_quant_edgetpu.tflite data/banana.dat

