#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
from datetime import datetime, timezone
from loguru import logger


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
    """Writes image-wise prediction outputs in JSON format.

    Schema version 2 adds:
    - image_index: ordered mapping of image_id -> sequential index.
    - summary_stats: lightweight aggregate statistics over all predictions.
    """

    def write(self, predictions, metadata=None):
        # Build image_id-based sequential index (sorted for reproducibility).
        sorted_ids = sorted(predictions.keys())
        image_index = {str(img_id): idx for idx, img_id in enumerate(sorted_ids)}

        # Compute lightweight summary statistics.
        total_images = len(predictions)
        images_with_detections = 0
        total_detections = 0
        all_scores = []
        per_category_counts = {}
        for pred in predictions.values():
            scores = pred.get("scores", [])
            if scores:
                images_with_detections += 1
            total_detections += len(scores)
            all_scores.extend(scores)
            for cat in pred.get("categories", []):
                key = str(cat)
                per_category_counts[key] = per_category_counts.get(key, 0) + 1

        summary_stats = {
            "total_images": total_images,
            "images_with_detections": images_with_detections,
            "total_detections": total_detections,
            "mean_score": float(sum(all_scores) / len(all_scores)) if all_scores else 0.0,
            "per_category_counts": per_category_counts,
        }

        payload = {
            "schema_version": 2,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
            "summary_stats": summary_stats,
            "image_index": image_index,
            "predictions": {str(k): v for k, v in predictions.items()},
        }
        predictions_path = os.path.join(self.output_dir, "predictions.json")
        with open(predictions_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        return {"predictions_path": predictions_path}


class WriterManager:
    """Manages and dispatches to multiple EvaluationWriter instances.

    Usage::

        manager = WriterManager(output_dir)
        manager.register("summary", SummaryWriter(output_dir))
        manager.register("predictions", PredictionWriter(output_dir))
        artifacts = manager.write_all(
            summary=summary, ap50_95=ap50_95, ap50=ap50,
            predictions=output_data, metadata=metadata,
        )
    """

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self._writers = {}

    def register(self, name: str, writer: EvaluationWriter) -> "WriterManager":
        """Register a writer under *name*. Returns self for chaining."""
        self._writers[name] = writer
        return self

    def write_all(self, summary, ap50_95, ap50, predictions=None, metadata=None):
        """Invoke all registered writers and return collected artifacts.

        Args:
            summary (str): Evaluation summary text.
            ap50_95 (float): COCO AP IoU=0.50:0.95.
            ap50 (float): COCO AP IoU=0.50.
            predictions (dict, optional): image_id-keyed prediction dict.
            metadata (dict, optional): Run-level metadata attached to each artifact.

        Returns:
            dict: Mapping of writer name -> artifacts dict returned by each writer.
        """
        all_artifacts = {}
        for name, writer in self._writers.items():
            if isinstance(writer, SummaryWriter):
                artifacts = writer.write(summary, ap50_95, ap50, metadata=metadata)
            elif isinstance(writer, PredictionWriter):
                if predictions is None:
                    logger.warning(
                        "WriterManager: PredictionWriter '{}' skipped — no predictions provided.",
                        name,
                    )
                    continue
                artifacts = writer.write(predictions, metadata=metadata)
            else:
                raise TypeError(
                    "WriterManager: unhandled writer type '{}' for '{}'. "
                    "Register a SummaryWriter or PredictionWriter.".format(
                        type(writer).__name__, name
                    )
                )
            all_artifacts[name] = artifacts
        return all_artifacts
