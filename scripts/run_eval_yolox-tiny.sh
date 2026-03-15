#! /bin/bash

EVAL_MODE="file"

BASE_CMD="python -m tools.eval -n yolox-tiny -c weights/yolox_tiny.pth -b 64 -d 1 --conf 0.001"

if [ "$EVAL_MODE" = "file" ]; then
	EVAL_OUT_DIR="YOLOX_outputs/yolox_tiny/eval"
    mkdir -p "$EVAL_OUT_DIR"
	docker compose run --rm yolox \
		$BASE_CMD --eval-out "$EVAL_OUT_DIR" --save-predictions
else
	docker compose run --rm yolox \
		$BASE_CMD
fi

