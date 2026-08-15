"""
Cyber Frame Camera
===================
Dua tangan bentuk 'L' -> bingkai cyber + filter di dalamnya.
  1  [L + L]        Satukan dua tangan L = bingkai, tarik = buka.
  2  [2 CUBIT]      Dua tangan cubit serentak = ganti filter.
  3  [KETAPEL]      Peace + Cubit ditarik = Y-shape; LEPAS cubit = ganti filter.
  4  [TELUNJUK]     Telunjuk ketat (tahan) di mode GAMBAR = gambar.
  5  [G]            Ganti mode LENSA <-> GAMBAR (keyboard).

Kontrol keyboard:
  G  - mode GAMBAR on/off
  F  - ambil foto (simpan ke foto/)
  C  - bersihkan kanvas (mode GAMBAR)
  U  - undo (mode GAMBAR)
  B  - ganti warna pena
  V  - tebalin pena   X - tipisin pena
  S  - reset posisi kanvas
  P  - ganti filter manual
  ESC- keluar
"""
import time

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_tasks
from mediapipe.tasks.python import vision

from src import lensa as lensa_mod
from src import gambar as gambar_mod
from src.config import MODEL, MAX_HAND, AMBANG_FOTO, DETECT_W, DETECT_H, LENSA, AMUNISI, PENA
from src import overlays
from src.gesture import build_info


def main():
    if not __import__("os").path.exists(MODEL):
        print(f"Model tidak ada: {MODEL}")
        return 1

    base = mp_tasks.BaseOptions(model_asset_path=MODEL, delegate=mp_tasks.BaseOptions.Delegate.CPU)
    hand_landmarker = vision.HandLandmarker.create_from_options(vision.HandLandmarkerOptions(
        base_options=base,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=MAX_HAND,
        min_hand_detection_confidence=AMBANG_FOTO,
        min_hand_presence_confidence=0.25,
        min_tracking_confidence=0.25,
    ))

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    modo = "LENSA"
    smooth_prev = []
    rng = np.random.default_rng(7)
    prev_ts = time.time()

    print("Cyber Frame Camera - Python")
    print("  L+L = bingkai  2 CUBIT = ganti filter  PEACE+CUBIT = KETAPEL  G = mode gambar  F = foto  P = filter  ESC = keluar")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        now = time.time()
        dt = now - prev_ts
        prev_ts = now
        ms = int(now * 1000)

        # deteksi di frame kecil biar TFLite cepat (FPS naik -> mulus), tampil tetap besar
        small = cv2.resize(frame, (DETECT_W, DETECT_H), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        res = hand_landmarker.detect_for_video(mp_img, ms)

        # normalised raw landmark
        hands = []
        if res.hand_landmarks:
            for lm in res.hand_landmarks:
                hands.append([(p.x, p.y) for p in lm])

        # smoothing (smoothenedHands)
        smoothed = []
        for i, arr in enumerate(hands):
            prev = smooth_prev[i] if i < len(smooth_prev) else None
            if prev is None or len(prev) != len(arr):
                smoothed.append([(p[0], p[1]) for p in arr])
                continue
            row = []
            for j, p in enumerate(arr):
                q = prev[j]
                d = ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5
                a = 0.95 if d > 0.02 else (0.85 if d > 0.005 else 0.7)
                row.append((p[0] * a + q[0] * (1 - a), p[1] * a + q[1] * (1 - a)))
            smoothed.append(row)
        smooth_prev = smoothed

        H, W = frame.shape[:2]
        # mirror display
        disp = cv2.flip(frame, 1)
        info_arr = build_info(smoothed, W, H)

        if modo == "GAMBAR":
            disp = gambar_mod.render_gambar(disp, info_arr, now, W, H)
        else:
            lensa_mod.render_lensa(disp, info_arr, now, W, H, rng)

        # flash
        if overlays.flash > 0:
            overlays.flash -= dt
            a = min(1.0, overlays.flash * 8)
            disp = cv2.addWeighted(disp, 1 - 0.6 * a, disp, 0, 0)
        overlays.draw_hud(disp, f"FPS {int(1.0 / max(dt, 1e-6))}  [{modo}]  {LENSA[lensa_mod.idx_lensa][0]}",
                 14, 32, 0.7, (111, 112, 120))

        cv2.imshow("Cyber Frame Camera", disp)

        key = cv2.waitKey(1) & 0xFF
        if key in (27, ord("q")):
            break
        elif key in (ord("g"), ord("G")):
            gambar_mod.reset_gambar_state()
            modo = "GAMBAR" if modo == "LENSA" else "LENSA"
        elif key in (ord("f"), ord("F")):
            overlays.take_foto(disp)
        elif key in (ord("c"), ord("C")) and modo == "GAMBAR":
            gambar_mod.clear_kanvas()
        elif key in (ord("u"), ord("U")) and modo == "GAMBAR":
            gambar_mod.undo_gambar(W, H)
        elif key in (ord("b"), ord("B")) and modo == "GAMBAR":
            gambar_mod.idx_pena = (gambar_mod.idx_pena + 1) % len(PENA)
        elif key in (ord("v"), ord("V")) and modo == "GAMBAR":
            gambar_mod.ketebalan = min(40, gambar_mod.ketebalan + 2)
        elif key in (ord("x"), ord("X")) and modo == "GAMBAR":
            gambar_mod.ketebalan = max(1, gambar_mod.ketebalan - 2)
        elif key in (ord("s"), ord("S")) and modo == "GAMBAR":
            gambar_mod.seret = [0, 0]
        elif key in (ord("p"), ord("P")):
            lensa_mod.amunisi_on = not lensa_mod.amunisi_on
            if lensa_mod.amunisi_on and lensa_mod.amunisi_kind is None:
                lensa_mod.amunisi_kind = AMUNISI[lensa_mod.amunisi_idx][1]
            print(f"[AMUNISI] {'ON' if lensa_mod.amunisi_on else 'OFF'} -> {AMUNISI[lensa_mod.amunisi_idx][0]}")
        elif key in (ord("n"), ord("N")) and lensa_mod.amunisi_on:
            lensa_mod.amunisi_idx = (lensa_mod.amunisi_idx + 1) % len(AMUNISI)
            lensa_mod.amunisi_kind = AMUNISI[lensa_mod.amunisi_idx][1]
            print(f"[AMUNISI] ganti -> {AMUNISI[lensa_mod.amunisi_idx][0]}")

    cap.release()
    cv2.destroyAllWindows()
    hand_landmarker.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())