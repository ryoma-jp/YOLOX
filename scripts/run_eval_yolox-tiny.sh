#! /bin/bash

python -m tools.eval -n  yolox-tiny -c weights/yolox_tiny.pth -b 64 -d 1 --conf 0.001
