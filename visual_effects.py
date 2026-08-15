"""
Visual effects for two-hand rectangle HUD - OPTIMIZED
"""
import cv2
import numpy as np
from typing import Tuple


class RectangleEffects:
    """Create visual effects for rectangle HUD - Performance optimized"""

    EFFECTS = [
        "Edge Detection",
        "Thermal",
        "Depth Map",
        "Inverted",
        "Pixelated",
        "Rainbow Wave",
    ]

    def __init__(self):
        self.time = 0
        self.threshold_mode = 0

    def update(self):
        """Update animation time"""
        self.time += 1

    def change_mode(self) -> str:
        """Cycle through threshold modes"""
        self.threshold_mode = (self.threshold_mode + 1) % len(self.EFFECTS)
        return self.EFFECTS[self.threshold_mode]

    def get_effect_name(self) -> str:
        return self.EFFECTS[self.threshold_mode]

    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Apply current visual effect to frame"""
        mode = self.threshold_mode

        if mode == 0:  # Edge Detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        elif mode == 1:  # Thermal
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return cv2.applyColorMap(gray, cv2.COLORMAP_JET)

        elif mode == 2:  # Depth Map
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (21, 21), 0)
            return cv2.applyColorMap(blurred, cv2.COLORMAP_HOT)

        elif mode == 3:  # Inverted
            return cv2.bitwise_not(frame)

        elif mode == 4:  # Pixelated
            h, w = frame.shape[:2]
            pixel_size = 14
            small_w, small_h = max(1, w // pixel_size), max(1, h // pixel_size)
            small = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
            return cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        elif mode == 5:  # Rainbow Wave
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 0] = (hsv[:, :, 0] + self.time * 3) % 180
            return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        return frame
