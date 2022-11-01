#!/bin/bash
#docker run --rm -it -v /Users/kafka/fun/edgetpu/edgetpu/compiler/x86_64:/compiler -v $PWD:/data --platform linux/amd64 ubuntu:focal /bin/bash
docker run --rm -it -v /Users/kafka/fun/edgetpu/edgetpu/compiler/x86_64:/compiler -v $PWD:/data --platform linux/amd64 ubuntu:focal /bin/bash -c 'cd /data && /compiler/edgetpu_compiler model.tflite -s'
