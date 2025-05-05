#! /bin/bash

python -m tools.eval -n  yolox-s -c weights/yolox_s.pth -b 64 -d 1 --conf 0.001
