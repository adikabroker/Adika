"""
scan_qr.py
============================================================
High-Accuracy Cadastre QR Scanning Engine
Multi-Pass Computer Vision Pipeline for Addis Ababa
Title Deed certificate verification.
============================================================
"""
from __future__ import annotations

import logging
import re
import time
import uuid as uuidlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    cv2 = None  # type: ignore
    np = None  # type: ignore

# --- Engine imports (graceful degradation if one is missing) ---
try:
    from pyzbar.pyzbar import decode as _pyzbar_decode
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False

try:
    import zxingcpp
    HAS_ZXING = True
except ImportError:
    HAS_ZXING = False

# ============================================================
# Configuration & Constants
# ============================================================
MAX_UPLOAD_BYTES = 10 * 1024 * 1024          # 10MB hard cap
MIN_DECODE_DIMENSION = 1200                  # upscale target (longest edge)
MIN_QR_AREA_RATIO = 0.005                    # candidate contour min area vs frame
KERNEL_REFERENCE_DIM = 600                   # morphological kernel scaling base
ALLOWED_DOMAIN = "addislandfarm.gov.et"
UUID_REGEX = re.compile(
    r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}'
    r'-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
)

logger = logging.getLogger("scan_qr")


class ScanStatus(str, Enum):
    RESOLVED = "resolved"
    FAILED_NO_QR = "failed_no_qr_resolved"
    FAILED_UNRECOGNIZED = "failed_unrecognized_payload"
    FAILED_INVALID_INPUT = "failed_invalid_input"


@dataclass
class ScanResult:
    status: ScanStatus
    url: Optional[str] = None
    raw_payload: Optional[str] = None
    reason: Optional[str] = None
    pass_name: Optional[str] = None
    duration_ms: int = 0
    attempts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "status": self.status.value,
            "url": self.url,
            "raw_payload": self.raw_payload,
            "reason": self.reason,
            "pass": self.pass_name,
            "duration_ms": self.duration_ms,
            "attempts": self.attempts,
        }


# ============================================================
# Section 1 — Preprocessing primitives
# ============================================================
def load_image(image_bytes: bytes):
    """Decode bytes -> BGR image with validation."""
    if not HAS_CV2:
        raise ValueError("OpenCV (cv2) is not installed on this server.")
    if not image_bytes:
        raise ValueError("Empty upload.")
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Upload exceeds {MAX_UPLOAD_BYTES // (1024*1024)}MB limit.")
    np_img = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Unsupported or corrupted image data.")
    return img


def normalize_scale(img):
    """Upscale high-density small-crop QR images."""
    h, w = img.shape[:2]
    longest = max(h, w)
    if longest < MIN_DECODE_DIMENSION:
        scale = MIN_DECODE_DIMENSION / longest
        img = cv2.resize(img, (int(w * scale), int(h * scale)),
                         interpolation=cv2.INTER_CUBIC)
    return img


def to_clean_gray(img):
    """Grayscale -> Non-local-means denoise -> CLAHE local contrast boost."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(
        gray, None, h=10, templateWindowSize=7, searchWindowSize=21
    )
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    return gray


# ============================================================
# Section 2 — Perspective correction
# ============================================================
def warp_qr_candidates(gray):
    """Detect large quadrilateral contours and perspective-warp into top-down view."""
    h, w = gray.shape[:2]
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edges = cv2.dilate(edges, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    warped = []
    for c in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
        area = cv2.contourArea(c)
        if area < h * w * MIN_QR_AREA_RATIO:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) != 4:
            continue
        pts = approx.reshape(4, 2).astype(np.float32)
        s = pts.sum(axis=1)
        d = np.diff(pts, axis=1).ravel()
        ordered = np.array([
            pts[np.argmin(s)], pts[np.argmin(d)],
            pts[np.argmax(s)], pts[np.argmax(d)]
        ], dtype=np.float32)
        width = max(np.linalg.norm(ordered[1] - ordered[0]),
                    np.linalg.norm(ordered[2] - ordered[3]))
        height = max(np.linalg.norm(ordered[3] - ordered[0]),
                     np.linalg.norm(ordered[2] - ordered[1]))
        if width < 40 or height < 40:
            continue
        dst = np.array([[0, 0], [width - 1, 0],
                        [width - 1, height - 1], [0, height - 1]],
                       dtype=np.float32)
        M = cv2.getPerspectiveTransform(ordered, dst)
        warped_img = cv2.warpPerspective(gray, M, (int(width), int(height)))
        wh, ww = warped_img.shape[:2]
        if max(wh, ww) < MIN_DECODE_DIMENSION:
            sc = MIN_DECODE_DIMENSION / max(wh, ww)
            warped_img = cv2.resize(warped_img, (int(ww * sc), int(wh * sc)),
                                    interpolation=cv2.INTER_CUBIC)
        warped.append(("warp", warped_img))
    return warped


# ============================================================
# Section 3 — Variant generation & dual-engine decoding
# ============================================================
def build_variants(gray):
    """Enumerate preprocessing variants."""
    variants = [("gray", gray)]
    adaptive = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, blockSize=15, C=8
    )
    k = max(2, max(gray.shape[:2]) // KERNEL_REFERENCE_DIM)
    kernel = np.ones((k, k), np.uint8)
    morphed = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
    _, otsu = cv2.threshold(cv2.GaussianBlur(gray, (3, 3), 0), 0, 255,
                            cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    inverted = cv2.bitwise_not(morphed)
    variants += [
        ("adaptive_thresh", adaptive),
        ("morph_close", morphed),
        ("otsu", otsu),
        ("inverted_morph", inverted),
    ]
    return variants


def _decode_pyzbar(img) -> Optional[str]:
    if not HAS_PYZBAR:
        return None
    results = _pyzbar_decode(img)
    for r in results:
        try:
            return r.data.decode("utf-8")
        except UnicodeDecodeError:
            continue
    return None


def _decode_zxing(img) -> Optional[str]:
    if not HAS_ZXING:
        return None
    try:
        results = zxingcpp.read_barcodes(img)
    except Exception:
        return None
    for r in results:
        if r.format == zxingcpp.BarcodeFormat.QRCode:
            return r.text
    return results[0].text if results else None


ENGINES = [
    ("pyzbar", _decode_pyzbar),
    ("zxing", _decode_zxing),
]


# ============================================================
# Section 4 — Strict payload sanitization
# ============================================================
def parse_verification_payload(raw_payload: Optional[str]):
    """Strict UUID or active domain parser."""
    if not raw_payload:
        return None, "QR code could not be resolved. Please capture a clearer photo."
    payload = raw_payload.strip()
    m = UUID_REGEX.search(payload)
    if m:
        candidate = m.group(0).lower()
        if candidate.count("0") == len(candidate.replace("-", "")):
            return None, "Degenerate certificate UUID detected."
        url = f"https://{ALLOWED_DOMAIN}/verify/{candidate}"
        logger.info("Sanitized payload -> active UUID %s", candidate)
        return url, None
    if ALLOWED_DOMAIN in payload and payload.lower().startswith(("http://", "https://")):
        return payload, None
    return None, "Unrecognized or legacy document QR code."


# ============================================================
# Section 5 — Orchestration endpoint core
# ============================================================
def scan_certificate_qr(image_bytes: bytes) -> ScanResult:
    start = time.monotonic()
    attempts: list = []
    last_reject: Optional[str] = None

    if not HAS_CV2:
        return ScanResult(
            status=ScanStatus.FAILED_INVALID_INPUT,
            reason="OpenCV is not installed. Install opencv-python-headless.",
            duration_ms=_ms(start),
        )
    if not HAS_PYZBAR and not HAS_ZXING:
        return ScanResult(
            status=ScanStatus.FAILED_INVALID_INPUT,
            reason="No QR decoder available. Install pyzbar and/or zxing-cpp.",
            duration_ms=_ms(start),
        )

    try:
        img = load_image(image_bytes)
    except ValueError as exc:
        return ScanResult(status=ScanStatus.FAILED_INVALID_INPUT,
                          reason=str(exc), duration_ms=_ms(start))

    _ = uuidlib.uuid4()
    img = normalize_scale(img)
    gray = to_clean_gray(img)

    search_images = [("full_frame", gray)]
    search_images.extend(warp_qr_candidates(gray))

    for region_name, region in search_images:
        variants = [("warp_pass", region)] if region_name == "warp" else build_variants(region)
        for v_item in variants:
            vname_str = v_item[0]
            variant_matrix = v_item[1]
            vname = f"{region_name}/{vname_str}"
            for ename, engine in ENGINES:
                payload = None
                try:
                    payload = engine(variant_matrix)
                except Exception as exc:
                    attempts.append(f"{vname}+{ename}:ERROR:{type(exc).__name__}")
                    continue
                attempts.append(f"{vname}+{ename}:{'hit' if payload else 'miss'}")
                if payload:
                    url, err = parse_verification_payload(payload)
                    if url:
                        return ScanResult(
                            status=ScanStatus.RESOLVED,
                            url=url, raw_payload=payload,
                            pass_name=f"{vname}+{ename}",
                            duration_ms=_ms(start), attempts=attempts,
                        )
                    last_reject = err

    return ScanResult(
        status=ScanStatus.FAILED_NO_QR,
        reason=(last_reject if last_reject else "QR code could not be resolved. Please capture a clearer photo."),
        duration_ms=_ms(start), attempts=attempts,
    )


def _ms(start: float) -> int:
    return int((time.monotonic() - start) * 1000)
