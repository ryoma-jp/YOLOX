#! /bin/bash

python tools/train.py -f exps/custom/yolox_tiny.py -d 1 -b 64 --fp16 -o -c weights/yolox_tiny.pth
