import unittest
import cv2
import numpy as np
from analysis import measure


class AnalysisTest(unittest.TestCase):
    def test_focus_and_compression(self):
        rng = np.random.default_rng(21)
        image = rng.integers(30, 220, (256, 256), dtype=np.uint8)
        cv2.circle(image, (80, 150), 48, 32, -1)
        def features(frame, quality):
            return measure(cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])[1].tobytes())
        original = features(image, 95)
        compressed = features(image, 70)
        blurred = features(cv2.GaussianBlur(image, (13, 13), 3), 90)
        self.assertLess((int(original["hash"], 16) ^ int(compressed["hash"], 16)).bit_count(), 8)
        self.assertLess(blurred["sharp"], original["sharp"] / 4)
