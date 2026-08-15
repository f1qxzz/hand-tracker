"""Mode LENSA: bingkai dua tangan + filter + auto-foto + ketapel."""
import math

import cv2
import numpy as np

from .config import (
    AMUNISI, SLIDE_FRAMES, FLASH_FRAMES, LENSA, HAND_CONNECTIONS,
    TAHAN_FOTO, TAHAN_QUAD_HILANG, DEBUG_PINCH,
)
from .filters import filter_frame, filter_amunisi
from .gesture import is_pinch, is_peace, is_l, nama_gesture
from .geometry import jarak, get_bounds, smooth_polygon
from .ketapel import (
    draw_ketapel, draw_ammo_hud, spawn_proyektil, update_render_proyektil,
)
from .overlays import take_foto, draw_hud, draw_ring

# state mode LENSA
prev_quad = None
diam_mulai = None
pinch_sampai = 0
idx_lensa = 0
smoothed_quad = None
quad_kosong_sejak = 0.0

# state KETAPEL
ketapel_sebelum_pinch = False   # state KETAPEL: pinch masih ditahan frame kemarin
ketapel_flash = 0               # frame countdown flash putih saat fire
ketapel_last_C = None           # posisi pinch terakhir saat HOLD (buat arah tembak)
ketapel_last_fork = None        # titik tengah garpu peace saat HOLD (arah tembak)
ketapel_proyektil = None        # bola yang meluncur; None = gak ada
ketapel_shockwave = None        # ring ledakan: dict x,y,r,a saat fire
amunisi_on = False
amunisi_idx = 0       # peluru berikutnya (yang ditampilkan saat HOLD)
amunisi_kind = None   # filter layer yang lagi aktif di seluruh layar
amunisi_slide = 0     # countdown slide-in layer setelah fire
amunisi_dir = (0.0, 0.0)        # arah tembak unit (dari C ke fork) buat slide-in


def render_lensa(frame, info, time_s, W, H, rng):
    global prev_quad, diam_mulai, pinch_sampai, idx_lensa
    global ketapel_sebelum_pinch, ketapel_flash
    global ketapel_last_C, ketapel_last_fork, ketapel_proyektil
    global amunisi_on, amunisi_idx, amunisi_kind
    global ketapel_shockwave, amunisi_slide, amunisi_dir
    global smoothed_quad, quad_kosong_sejak

    # ── deteksi KETAPEL: peace di satu tangan + pinch di tangan lain ──
    # peace kiri + pinch kanan (kayak di video); cek pinch dulu biar peace gak ketimpa
    peace_hand = None
    pinch_hand = None
    for hand, f, px in info:
        if is_pinch(hand):
            if pinch_hand is None:
                pinch_hand = px
        elif is_peace(f):
            if peace_hand is None:
                peace_hand = px
    ketapel_aktif = peace_hand is not None and pinch_hand is not None

    # amunisi aktif membungkus seluruh layar (layer bawah; overlay digambar di atasnya).
    # pas ketapel ditarik, background balik normal biar Y-shape + tarikan keliatan jelas.
    if amunisi_on and amunisi_kind is not None and not ketapel_aktif:
        frame[:] = filter_amunisi(frame, amunisi_kind, time_s)
        if amunisi_slide > 0:  # slide-in dari arah proyeksi tembakan
            amt = amunisi_slide / SLIDE_FRAMES * 40
            frame[:] = np.roll(frame, (int(amunisi_dir[1] * amt), int(amunisi_dir[0] * amt)), (0, 1))
            amunisi_slide -= 1

    # ── Quad dari dua tangan (thumb+index tip), tak peduli gesture-nya ──
    quad = None
    if len(info) >= 2:
        ha, hb = [h for h, _, _ in info][:2]
        a_t = ha[4]; b_t = hb[4]
        a_i = ha[8]; b_i = hb[8]
        quad = [
            [(1 - a_t[0]) * W, a_t[1] * H],
            [(1 - b_t[0]) * W, b_t[1] * H],
            [(1 - b_i[0]) * W, b_i[1] * H],
            [(1 - a_i[0]) * W, a_i[1] * H],
        ]
    # smoothing + hold: quad ditahan sesaat biar ga patah-patah saat deteksi ngedrop
    if quad is not None:
        poin = smooth_polygon(smoothed_quad, quad, k=0.4)
        smoothed_quad = poin
        quad_kosong_sejak = time_s
    elif smoothed_quad is not None and (time_s - quad_kosong_sejak) < TAHAN_QUAD_HILANG:
        poin = smoothed_quad
    else:
        poin = None
        smoothed_quad = None

    # saat ketapel aktif: quad + auto-foto di-skip biar peace+pinch fokus ke Y-shape
    if poin and not ketapel_aktif:
        b = get_bounds(poin)
        diag = (jarak(poin[2], poin[0]) + jarak(poin[3], poin[1])) / 2
        skala = W / 960.0
        min_buka = 14 * skala
        if diag < min_buka:
            c = [sum(p[0] for p in poin) / 4, sum(p[1] for p in poin) / 4]
            draw_ring(frame, c[0], c[1], 24, 0, (0, 235, 255))
            draw_hud(frame, "TARIK UNTUK MEMBUKA", c[0] - 160, c[1] - 28, 0.8, (0, 235, 255))
            diam_mulai = None
        else:
            gerak = 0.0
            if prev_quad is not None:
                gerak = max(jarak(poin[i], prev_quad[i]) for i in range(4))
            prev_quad = [tuple(p) for p in poin]
            masih_gerak = gerak > 9 * skala
            if masih_gerak or diam_mulai is None:
                diam_mulai = time_s
            sisa = TAHAN_FOTO - (time_s - diam_mulai)
            maju = min(1.0, max(0.0, 1 - sisa / TAHAN_FOTO))

            # filter di dalam polygon — cuma di bbox lensa biar ringan
            xs = [p[0] for p in poin]
            ys = [p[1] for p in poin]
            x0, x1 = max(0, int(min(xs)) - 4), min(W, int(max(xs)) + 4)
            y0, y1 = max(0, int(min(ys)) - 4), min(H, int(max(ys)) + 4)
            crop = frame[y0:y1, x0:x1]
            m2 = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
            pts2 = np.array(poin, dtype=np.int32) - np.array([x0, y0])
            cv2.fillPoly(m2, [pts2.reshape((-1, 1, 2))], 255)
            filt = filter_frame(crop, LENSA[idx_lensa][1], time_s, rng)
            crop[m2 > 0] = filt[m2 > 0]

            # border cyber
            pts = np.array(poin, dtype=np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, (255, 242, 95), max(2, W // 560), cv2.LINE_AA)
            cv2.polylines(frame, [pts], True, (0, 222, 255), max(1, W // 1200), cv2.LINE_AA)
            for p in poin:
                cv2.circle(frame, (int(p[0]), int(p[1])), max(3, W // 300), (255, 248, 145), -1)
            draw_hud(frame, f"{LENSA[idx_lensa][0]} // ACTIVE",
                     int(b["left"]) + 8, max(24, int(b["top"]) - 8), 0.7, (46, 250, 151))

            # progress bar foto
            a = poin[0]; b2 = poin[1]
            cv2.line(frame, (int(a[0]), int(a[1])),
                     (int(a[0] + (b2[0] - a[0]) * maju), int(a[1] + (b2[1] - a[1]) * maju)),
                     (0, 180, 255) if sisa > 1 else (255, 0, 200), 4, cv2.LINE_AA)
            if sisa <= 0:
                take_foto(frame)
                diam_mulai = None
                prev_quad = None
            elif sisa < TAHAN_FOTO - 0.25:
                ang = int(math.ceil(sisa))
                draw_hud(frame, f"{ang}",
                         int(poin[0][0] + (poin[2][0] - poin[0][0]) / 2 - 12),
                         int(poin[0][1] + (poin[2][1] - poin[0][1]) / 2 + 40), 1.6,
                         (0, 180, 255) if sisa > 1 else (255, 0, 200))
    else:
        diam_mulai = None
        prev_quad = None

    # ── KETAPEL: peace + pinch ditarik → Y-shape; lepas pinch saat peace = TEMBAK ──
    if ketapel_aktif:
        A = (peace_hand[8][0], peace_hand[8][1])
        B = (peace_hand[12][0], peace_hand[12][1])
        C = ((pinch_hand[4][0] + pinch_hand[8][0]) / 2,
             (pinch_hand[4][1] + pinch_hand[8][1]) / 2)
        ketapel_last_C = C
        ketapel_last_fork = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        draw_ketapel(frame, A, B, C, AMUNISI[amunisi_idx][0], time_s)
        draw_ammo_hud(frame, AMUNISI[amunisi_idx][0])
        ketapel_sebelum_pinch = True
    elif ketapel_sebelum_pinch and peace_hand is not None:
        # FIRE: pinch dilepas, peace masih ada → amunisi nempel di seluruh layar
        amunisi_on = True
        amunisi_kind = AMUNISI[amunisi_idx][1]
        amunisi_idx = (amunisi_idx + 1) % len(AMUNISI)
        amunisi_slide = SLIDE_FRAMES
        ketapel_flash = FLASH_FRAMES
        ketapel_sebelum_pinch = False
        if ketapel_last_C is not None and ketapel_last_fork is not None:
            ketapel_proyektil = spawn_proyektil(ketapel_last_C, ketapel_last_fork)
            dx = ketapel_last_fork[0] - ketapel_last_C[0]
            dy = ketapel_last_fork[1] - ketapel_last_C[1]
            dd = math.hypot(dx, dy)
            amunisi_dir = (dx / dd, dy / dd) if dd else (0.0, 0.0)
            ketapel_shockwave = {"x": ketapel_last_C[0], "y": ketapel_last_C[1], "r": 12, "a": 1.0}
        print(f"[BANG!] KETAPEL DETEMBAKI! Amunisi -> {AMUNISI[(amunisi_idx - 1) % len(AMUNISI)][0]}")
    else:
        ketapel_sebelum_pinch = False

    # proyektil bola tetap jalan walau karet udah lepas
    if ketapel_proyektil is not None:
        ketapel_proyektil = update_render_proyektil(frame, ketapel_proyektil, W, H)

    # shockwave ring ledakan dari titik C setelah fire
    if ketapel_shockwave is not None:
        s = ketapel_shockwave
        s["r"] += 20
        s["a"] -= 0.12
        if s["a"] > 0:
            x, y = int(s["x"]), int(s["y"])
            cv2.circle(frame, (x, y), int(s["r"]), (0, 255, 220), 2, cv2.LINE_AA)
            cv2.circle(frame, (x, y), int(s["r"] * 0.6), (255, 255, 255), 1, cv2.LINE_AA)
        else:
            ketapel_shockwave = None

    # flash putih singkat setelah fire
    if ketapel_flash > 0:
        a = 0.35 * (ketapel_flash / FLASH_FRAMES)
        frame[:] = cv2.addWeighted(frame, 1 - a, np.full_like(frame, 255), a, 0)
        ketapel_flash -= 1

    # ── 2 pinch serentak ganti filter (debounce) ──
    n_pinch = sum(1 for hand, _, _ in info if is_pinch(hand))
    if n_pinch >= 2 and time_s > pinch_sampai:
        idx_lensa = (idx_lensa + 1) % len(LENSA)
        pinch_sampai = time_s + 0.8

    # ── skeleton + tips ──
    for _, f, px in info:
        ok = is_l(f)
        col = (120, 90, 150) if ok else (105, 80, 95)
        for c in HAND_CONNECTIONS:
            cv2.line(frame, (int(px[c[0]][0]), int(px[c[0]][1])),
                     (int(px[c[1]][0]), int(px[c[1]][1])), col, 1, cv2.LINE_AA)
        for i in (4, 8):
            cv2.circle(frame, (int(px[i][0]), int(px[i][1])), 7,
                       (0, 235, 255) if ok else (105, 80, 105), -1)

    # ── debug HUD per tangan (matikan kalau sudah jalan) ──
    dy = 0
    for hand, f, px in info:
        dx = px[0][0]
        g = nama_gesture(f)
        if is_pinch(hand):
            g = "PINCH"
        ratio = jarak(hand[4], hand[8]) / max(jarak(hand[0], hand[9]), 1e-6)
        dbg = f"{g} {ratio:.2f}"
        cv2.putText(frame, dbg, (int(max(dx - 40, 4)), 20 + dy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 90, 220), 2)
        dy += 18
    if DEBUG_PINCH:
        cv2.putText(frame, f"n_pinch={sum(1 for h,_,_ in info if is_pinch(h))}",
                    (10, H - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 90, 220), 2)
    if not info:
        draw_hud(frame, "BENTUK 'L' DUA TANGAN, SATUKAN, LALU TARIK",
                 22, H - 30, 0.7, (111, 112, 120))