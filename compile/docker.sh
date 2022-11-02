#!/bin/bash
#docker run --rm -it --cap-add=SYS_PTRACE --security-opt seccomp=unconfined -v /Users/kafka/fun/edgetpu/edgetpu/compiler/aarch64:/compiler -v $PWD:/data --platform linux/aarch64 ubuntu:focal /bin/bash
docker run --rm -it -v /Users/kafka/fun/edgetpu/edgetpu/compiler/aarch64:/compiler -v $PWD:/data --platform linux/aarch64 ubuntu:focal /bin/bash -c 'cd /data && /compiler/edgetpu_compiler model.tflite -s'
#docker run --rm -it -v /Users/kafka/fun/edgetpu/edgetpu/compiler/x86_64:/compiler -v $PWD:/data --platform linux/amd64 ubuntu:focal /bin/bash -c 'cd /data && /compiler/edgetpu_compiler model.tflite -s'

# 0xaaaaaa9a0000 is base address
# set follow-fork-mode child
