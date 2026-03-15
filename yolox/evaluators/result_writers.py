#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
from datetime import datetime, timezone


class EvaluationWriter:
    """Base interface for writing evaluation artifacts."""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)


class SummaryWriter(EvaluationWriter):
    """Writes evaluation summary text and scalar metrics."""

    def write(self, summary: str, ap50_95: float, ap50: float, metadata=None):
        summary_path = os.path.join(self.output_dir, "summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary)

        payload = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "ap50_95": float(ap50_95),
                "ap50": float(ap50),
            },
            "metadata": metadata or {},
        }
        metrics_path = os.path.join(self.output_dir, "metrics.json")
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return {"summary_path": summary_path, "metrics_path": metrics_path}


class PredictionWriter(EvaluationWriter):
    """Writes image-wise prediction outputs in JSON format."""

    def write(self, predictions, metadata=None):
        payload = {
            "schema_version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "predictions": predictions,
        }
        predictions_path = os.path.join(self.output_dir, "predictions.json")
        with open(predictions_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return {"predictions_path": predictions_path}
