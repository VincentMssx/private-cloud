"""Measure the same bounded preview for each original."""
import cv2
import numpy as np

cv2.setNumThreads(1)


def measure(data):
    pixels = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_GRAYSCALE)
    if pixels is None:
        raise ValueError("invalid preview")
    small = cv2.resize(pixels, (32, 32), interpolation=cv2.INTER_AREA)
    frequencies = cv2.dct(small.astype(np.float32))[:8, :8].flatten()
    bits = frequencies > np.median(frequencies[1:])
    sharpness = cv2.Laplacian(pixels, cv2.CV_64F).var()
    clipping = np.mean((pixels < 8) | (pixels > 247))
    return {"hash": np.packbits(bits).tobytes().hex(), "sharp": round(float(sharpness), 2),
            "clipped": round(float(clipping), 4)}
