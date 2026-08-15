"""
Two-Hand Rectangle Tracker
--------------------------
Show both hands to create a floating rectangle between them.
The rectangle displays cool visual effects that follow your hands.

Controls:
  SPACE       - Pause / Resume
  M           - Manually change effect
  ESC         - Exit

Hand Gestures:
  🤏 PINCH    - Switch to next effect
  🔄 ROTATE   - Rectangle rotates with your hands
"""

import time
import math
import cv2
import mediapipe as mp
import numpy as np

from visual_effects import RectangleEffects


# ─── Helpers ──────────────────────────────────────────────────────────────────

def is_pinching(lm: dict, threshold: float = 38.0) -> bool:
    """Return True when thumb tip (4) and index tip (8) are close."""
    thumb = np.array(lm[4], dtype=np.float32)
    index = np.array(lm[8], dtype=np.float32)
    return float(np.linalg.norm(thumb - index)) < threshold


def compute_quad(p1, p2, height_ratio: float = 0.65) -> np.ndarray:
    """
    Build a rotated quadrilateral from two hand anchor points.
    p1, p2  – anchor points (wrist of each hand)
    Returns (4, 2) float32 corners: [TL, TR, BR, BL]
    """
    a = np.array(p1, dtype=np.float32)
    b = np.array(p2, dtype=np.float32)
    direction = b - a
    length = np.linalg.norm(direction)
    if length < 1e-3:
        return None

    unit = direction / length
    perp = np.array([-unit[1], unit[0]])   # 90° CCW
    half_h = length * height_ratio / 2.0

    return np.array([
        a + perp * half_h,   # TL
        b + perp * half_h,   # TR
        b - perp * half_h,   # BR
        a - perp * half_h,   # BL
    ], dtype=np.float32)


def warp_into_quad(frame: np.ndarray,
                   effect_frame: np.ndarray,
                   quad: np.ndarray) -> np.ndarray:
    """Paste effect_frame warped into the quad on top of frame."""
    h_src, w_src = effect_frame.shape[:2]
    fh, fw = frame.shape[:2]

    src_corners = np.float32([[0, 0], [w_src, 0], [w_src, h_src], [0, h_src]])
    M = cv2.getPerspectiveTransform(src_corners, quad)

    warped = cv2.warpPerspective(effect_frame, M, (fw, fh))

    mask = np.zeros((fh, fw), dtype=np.uint8)
    cv2.fillConvexPoly(mask, quad.astype(np.int32), 255)
    mask_3ch = cv2.merge([mask, mask, mask])

    result = np.where(mask_3ch > 0, warped, frame)

    # Glowing green border
    cv2.polylines(result, [quad.astype(np.int32)], isClosed=True,
                  color=(0, 255, 80), thickness=2, lineType=cv2.LINE_AA)

    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    mp_hands = mp.solutions.hands
    detector = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.45,
        min_tracking_confidence=0.35,
    )

    effects = RectangleEffects()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

    paused = False
    pinch_cooldown = 0
    PINCH_COOLDOWN = 22          # frames before next pinch is accepted
    prev_ts = time.time()

    # ── smoothing + hold state ──
    smoothed_hands = [None, None]   # list 2 x 21 (x,y) normalized EMA
    last_quad = None                # quad terakhir biar ga patah saat tangan sesaat ilang
    last_quad_t = 0.0
    QUAD_HOLD = 0.5                 # detik quad ditahan saat tangan tidak terdeteksi

    print("\nStarting...\n")
    print("Keyboard Shortcuts:")
    print("  SPACE - Pause")
    print("  M     - Manually change effect mode")
    print("  ESC   - Exit\n")
    print("💡 Instructions:")
    print("  - Show BOTH hands to camera")
    print("  - Rectangle instantly follows your hands")
    print("  - 🤏 PINCH to change effect")
    print("  - Rotate hands = rectangle rotates\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)        # mirror so it feels natural

        if not paused:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = detector.process(rgb)
            effects.update()

            if pinch_cooldown > 0:
                pinch_cooldown -= 1

            # ── landmarks + smoothing EMA ──
            hands_raw = results.multi_hand_landmarks or []
            smooth_ok = [False, False]
            lm = [None, None]
            for i, hl in enumerate(hands_raw[:2]):
                arr = [(lmk.x, lmk.y) for lmk in hl.landmark]
                prev = smoothed_hands[i]
                if prev is None:
                    smoothed_hands[i] = arr[:]
                else:
                    # alpha adaptif: gerak cepat -> ikut cepat, diam -> stabil
                    row = []
                    for j, p in enumerate(arr):
                        d = math.hypot(p[0] - prev[j][0], p[1] - prev[j][1])
                        a = 0.6 if d > 0.02 else (0.35 if d > 0.005 else 0.2)
                        row.append((p[0] * a + prev[j][0] * (1 - a),
                                    p[1] * a + prev[j][1] * (1 - a)))
                    smoothed_hands[i] = row
                lm[i] = {idx: (int(smoothed_hands[i][idx][0] * frame.shape[1]),
                               int(smoothed_hands[i][idx][1] * frame.shape[0]))
                         for idx in range(21)}
                smooth_ok[i] = True

            # ── quad: hold saat salah satu tangan sesaat ilang ──
            now = time.time()
            quad = None
            if smooth_ok[0] and smooth_ok[1]:
                quad = compute_quad(lm[0][0], lm[1][0])
                if quad is not None:
                    last_quad = quad
                    last_quad_t = now
            elif last_quad is not None and now - last_quad_t < QUAD_HOLD:
                quad = last_quad
            else:
                last_quad = None

            # ── Pinch to switch effect ──
            if pinch_cooldown == 0 and smooth_ok[0] and smooth_ok[1] and \
                    (is_pinching(lm[0]) or is_pinching(lm[1])):
                name = effects.change_mode()
                print(f"  Effect: {name}")
                pinch_cooldown = PINCH_COOLDOWN

            # ── Build & render quad ──
            if quad is not None:
                effect_out = effects.apply(frame.copy())
                frame = warp_into_quad(frame, effect_out, quad)

            # Draw small dots at wrists & fingertips
            for i in range(2):
                if smooth_ok[i]:
                    cv2.circle(frame, lm[i][0], 7, (0, 255, 80), -1)    # wrist
                    cv2.circle(frame, lm[i][4], 6, (0, 80, 255), -1)    # thumb
                    cv2.circle(frame, lm[i][8], 6, (255, 80, 0), -1)    # index

        # ── HUD ──
        now = time.time()
        fps = 1.0 / max(now - prev_ts, 1e-6)
        prev_ts = now

        cv2.putText(frame, f"FPS: {int(fps)}",
                    (14, 38), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 80), 2, cv2.LINE_AA)
        cv2.putText(frame, effects.get_effect_name(),
                    (14, 76), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 80), 2, cv2.LINE_AA)

        if paused:
            cv2.putText(frame, "PAUSED",
                        (14, 114), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 140, 255), 2, cv2.LINE_AA)

        cv2.imshow("Two-Hand Rectangle Tracker", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:               # ESC
            break
        elif key == 32:             # SPACE
            paused = not paused
        elif key in (ord("m"), ord("M")):
            name = effects.change_mode()
            print(f"  Effect: {name}")

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    main()
