"""Overlay HUD, ring, dan penyimpanan foto."""
import os
import time

import cv2

from .config import FOTO_DIR

flash = 0.0


def take_foto(frame):
    global flash
    flash = 0.12
    name = os.path.join(FOTO_DIR, f"cyberframe-{int(time.time() * 1000)}.png")
    cv2.imwrite(name, cv2.flip(frame, 1))  # un-mirror supaya foto orientasi natural
    return name


def draw_hud(frame, txt, x, y, s, warna=(240, 245, 250)):
    cv2.putText(frame, txt, (x, y), cv2.FONT_HERSHEY_SIMPLEX, s,
                (0, 0, 0), max(2, int(s)), cv2.LINE_AA)
    cv2.putText(frame, txt, (x, y), cv2.FONT_HERSHEY_SIMPLEX, s,
                warna, max(1, int(s / 2)), cv2.LINE_AA)


def draw_ring(frame, cx, cy, r, maju, warna):
    cv2.circle(frame, (int(cx), int(cy)), r, (55, 50, 62), 4, cv2.LINE_AA)
    if maju > 0:
        cv2.ellipse(frame, (int(cx), int(cy)), (r, r), -90, 0,
                    360 * min(1, maju), warna, 4, cv2.LINE_AA)