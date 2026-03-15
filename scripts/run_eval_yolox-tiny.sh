#! /bin/bash

EVAL_MODE="file"

BASE_CMD="python -m tools.eval -n yolox-tiny -c weights/yolox_tiny.pth -b 64 -d 1 --conf 0.001"

if [ "$EVAL_MODE" = "file" ]; then
	EVAL_OUT_DIR="YOLOX_outputs/yolox_tiny/eval"
    mkdir -p "$EVAL_OUT_DIR"
    rm -rf "$EVAL_OUT_DIR"/*
	docker compose run --rm yolox \
		$BASE_CMD --eval-out "$EVAL_OUT_DIR" --save-predictions
    
    docker compose run --rm yolox \
        python tools/visualize_eval_results.py \
            --predictions-path YOLOX_outputs/yolox_tiny/eval/predictions.json \
            --conf-threshold 0.3 \
            --nms-iou-threshold 0.5 \
            --images-dir datasets/COCO/val2017 \
            --annotations-path datasets/COCO/annotations/instances_val2017.json \
            --output-dir YOLOX_outputs/yolox_tiny/eval/vis_res \
            --image-id 397133
else
	docker compose run --rm yolox \
		$BASE_CMD
fi

