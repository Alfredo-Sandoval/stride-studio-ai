#!/usr/bin/env python3
# ---------------------------------------------------------------------------
#  stride_studio_ai/core/models.py – lightweight Ultralytics wrappers
#  Revision: 2025-04-30
# ---------------------------------------------------------------------------
from __future__ import annotations

# stdlib
from pathlib import Path
from typing import List, Tuple, Dict

# third-party
import cv2
import numpy as np
import torch
from ultralytics import YOLO

import logging

log = logging.getLogger("stride_studio.core.models")

__all__ = ["YoloPose", "YoloGeneric"]

# ─────────────────────────────────────────────────────────────────── pose ──
_SKELETON: List[Tuple[int, int]] = [
    (15, 13),
    (13, 11),
    (16, 14),
    (14, 12),
    (11, 12),
    (5, 11),
    (6, 12),
    (5, 6),
    (5, 7),
    (6, 8),
    (7, 9),
    (8, 10),
    (5, 3),
    (6, 4),
    (3, 1),
    (4, 2),
    (1, 2),
]
JOINT_COLOR = (0, 255, 0)  # lime
BONE_COLOR = (255, 255, 0)  # yellow
JOINT_R = 4
BONE_W = 3
CONF_TH = 0.05

# ───────────────────────────────────────────────────────────── shared cache ─
_MODEL_CACHE: Dict[str, YOLO] = {}


def _load_model(weights: str | Path, device: str | None = None) -> YOLO:
    """Load or fetch from cache."""
    w = str(weights)
    if w not in _MODEL_CACHE:
        path = Path(__file__).resolve().parent.parent / "models" / w
        if not path.is_file():
            raise FileNotFoundError(path)
        log.info("Loading model: %s on %s", path, device or "auto")
        _MODEL_CACHE[w] = YOLO(str(path)).to(
            device or "cuda:0" if torch.cuda.is_available() else "cpu"
        )
    return _MODEL_CACHE[w]


# ────────────────────────────────────────────────────────────── wrappers ───
class YoloPose:
    """
    Ultralytics **pose** checkpoint (17-keypoint COCO skeleton).

    Example
    -------
    >>> model = YoloPose("yolo11x-pose.pt")
    >>> frame_bgr = model(frame_bgr)        # annotated in-place
    """

    def __init__(
        self,
        ckpt: str | Path = "yolo11x-pose.pt",
        *,
        imgsz: int = 640,
        half: bool = False,
        device: str | None = None,
    ):
        self.ckpt = str(ckpt)
        self.model = _load_model(self.ckpt, device)
        if half and self.model.device.type == "cuda":
            self.model.half()
        self.imgsz = imgsz
        self.device = self.model.device

    @torch.inference_mode()
    def __call__(self, frame_bgr: np.ndarray) -> np.ndarray:
        res = self.model(
            frame_bgr, imgsz=self.imgsz, device=self.device, verbose=False
        )[0]

        kpts = res.keypoints.xy.cpu().numpy()  # (N,17,2)

        # Fix for tensor boolean ambiguity
        if res.keypoints.conf is not None:
            conf = res.keypoints.conf.cpu().numpy()
        else:
            conf = np.ones_like(kpts[..., 0])

        out = frame_bgr.copy()
        h, w = out.shape[:2]

        for pts, cf in zip(kpts, conf):
            if pts.shape[0] != 17:
                continue
            # bones
            for a, b in _SKELETON:
                if cf[a] < CONF_TH or cf[b] < CONF_TH:
                    continue
                ax, ay = map(int, pts[a])
                bx, by = map(int, pts[b])
                if 0 < ax < w and 0 < ay < h and 0 < bx < w and 0 < by < h:
                    cv2.line(out, (ax, ay), (bx, by), BONE_COLOR, BONE_W)
            # joints
            for (x, y), p in zip(pts, cf):
                if p >= CONF_TH and 0 < x < w and 0 < y < h:
                    cv2.circle(out, (int(x), int(y)), JOINT_R, JOINT_COLOR, -1)
        return out


class YoloGeneric:
    """
    Wrapper for Ultralytics **detection / segmentation / classification**
    checkpoints.

    It simply calls `.plot()` which already returns a BGR ndarray with the
    model's own overlay.
    """

    def __init__(self, ckpt: str | Path, *, device: str | None = None):
        self.ckpt = str(ckpt)
        self.model = _load_model(self.ckpt, device)
        self.device = self.model.device

    @torch.inference_mode()
    def __call__(self, frame_bgr: np.ndarray) -> np.ndarray:
        res = self.model(frame_bgr, device=self.device, verbose=False)[0]
        plotted = res.plot()  # always returns BGR ndarray
        return plotted if isinstance(plotted, np.ndarray) else frame_bgr
