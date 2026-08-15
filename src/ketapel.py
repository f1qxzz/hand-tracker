"""Render visual ketapel (busur, tali glow, partikel, bola energi, dll)."""
import math

import cv2
import numpy as np

from .geometry import jarak


def calc_stretch_pct(A, B, C):
    """Persentase tarikan ketapel: jarak pinch(C) dari tengah garpu peace(A-B)."""
    fm = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    fl = jarak(A, B)
    sd = jarak(C, fm)
    if fl < 1:
        return 0
    return int(min(sd / fl * 100, 100))


def tense_color(pct):
    """Hijau tenang -> kuning -> oranye -> merah seiring tegangan."""
    stops = [(50, 255, 50), (0, 220, 255), (0, 120, 255), (0, 40, 255)]
    ts = [0, 40, 70, 100]
    for i in range(3):
        if pct <= ts[i + 1]:
            t = (pct - ts[i]) / max(ts[i + 1] - ts[i], 1)
            return tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * t) for k in range(3))
    return stops[-1]


def glow_line(frame, p0, p1, col, th, blink=1.0):
    """3 lapis: halo gelap tebal -> warna utama -> inti putih/panas."""
    p0 = (int(p0[0]), int(p0[1])); p1 = (int(p1[0]), int(p1[1]))
    cv2.line(frame, p0, p1, (0, 45, 12), th + 8, cv2.LINE_AA)
    cv2.line(frame, p0, p1, (0, 105, 38), th + 5, cv2.LINE_AA)
    main = tuple(int(c * blink) for c in col)
    cv2.line(frame, p0, p1, main, th, cv2.LINE_AA)
    cv2.line(frame, p0, p1, (255, 255, 235), max(1, th // 2), cv2.LINE_AA)


def bezier_pts(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((int(x), int(y)))
    return pts


def partikel(frame, A, C, col, n, pct, time_s):
    """Titik energi mengalir dari garpu(A) ke pinch(C); akselerasi di dekat C."""
    speed = 0.06 + pct * 0.0012
    for i in range(n):
        u = (i / max(n, 1) + time_s * speed) % 1
        s = 1 - (1 - u) ** 1.5
        x = int(A[0] + (C[0] - A[0]) * s); y = int(A[1] + (C[1] - A[1]) * s)
        cv2.circle(frame, (x, y), max(1, int(1 + s * 2)), col, -1, cv2.LINE_AA)


def proyeksi(frame, C, M, pct):
    """Garis putus-putus dari C searah tembak (ke fork), panjang proporsional stretch."""
    dx, dy = M[0] - C[0], M[1] - C[1]
    d = math.hypot(dx, dy)
    if d < 1:
        return
    ux, uy = dx / d, dy / d
    L = 40 + pct * 1.6
    x, y, drawn = C[0], C[1], 0.0
    seg, gap = 8, 6
    while drawn < L:
        e = min(seg, L - drawn)
        cv2.line(frame, (int(x), int(y)), (int(x + ux * e), int(y + uy * e)), (50, 255, 50), 1, cv2.LINE_AA)
        x += ux * (e + gap); y += uy * (e + gap); drawn += e + gap


def garpu(frame, P, away, col):
    """Segitiga kecil di ujung garpu mengarah keluar (menjauhi tengah)."""
    ax, ay = away
    px, py = -ay, ax
    tip = (int(P[0] + ax * 12), int(P[1] + ay * 12))
    b1 = (int(P[0] + px * 6), int(P[1] + py * 6))
    b2 = (int(P[0] - px * 6), int(P[1] - py * 6))
    tri = np.array([tip, b1, b2], np.int32)
    cv2.fillPoly(frame, [tri], col)
    cv2.polylines(frame, [tri], True, (0, 0, 0), 1)


def bola_energi(frame, C, pct, col):
    """Pinch point jadi bola energi berlapis yang tumbuh seiring stretch."""
    r = 8 + 10 * pct / 100
    x, y = int(C[0]), int(C[1])
    cv2.circle(frame, (x, y), int(r + 6), (0, 45, 15), -1, cv2.LINE_AA)
    cv2.circle(frame, (x, y), int(r), col, -1, cv2.LINE_AA)
    cv2.circle(frame, (x, y), max(2, int(r * 0.4)), (255, 255, 235), -1, cv2.LINE_AA)


def spawn_proyektil(origin, target):
    """Bola ketapel dari origin (pinch) meluncur ke arah target (fork peace)."""
    ox, oy = origin
    dx = target[0] - ox
    dy = target[1] - oy
    d = math.hypot(dx, dy) or 1.0
    speed = min(30.0, max(12.0, d / 30.0 + 8.0))
    return {"x": ox, "y": oy, "vx": dx / d * speed, "vy": dy / d * speed,
            "trail": [], "r": 12}


def update_render_proyektil(frame, p, W, H):
    """Geser bola + trail neon hijau, return None kalau udah keluar layar."""
    p["x"] += p["vx"]
    p["y"] += p["vy"]
    p["trail"].append((p["x"], p["y"]))
    if len(p["trail"]) > 16:
        p["trail"].pop(0)
    if len(p["trail"]) > 1:
        pts = np.array(p["trail"], dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], False, (0, 255, 80), 5, cv2.LINE_AA)
    cv2.circle(frame, (int(p["x"]), int(p["y"])), p["r"], (0, 255, 80), -1, cv2.LINE_AA)
    cv2.circle(frame, (int(p["x"]), int(p["y"])), p["r"] - 4, (220, 255, 220), -1, cv2.LINE_AA)
    if (p["x"] < -60 or p["x"] > W + 60 or p["y"] < -60 or p["y"] > H + 60):
        return None
    return p


def draw_ketapel(frame, A, B, C, filter_name, time_s):
    """Ketapel upgrade: busur bezier responsif, glow 3 lapis, partikel, bola energi,
    color shift tegangan, ujung garpu tajam, garis proyeksi tembakan."""
    pct = calc_stretch_pct(A, B, C)
    col = tense_color(pct)
    blink = (0.6 + 0.4 * math.sin(time_s * 12)) if pct > 70 else 1.0
    M = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)

    # busur melengkung menjauhi C; makin ditarik makin lurus/tegang
    dx, dy = M[0] - C[0], M[1] - C[1]
    d = math.hypot(dx, dy) or 1
    depth = max(4, 30 * (1 - pct / 100))
    ctrl = (M[0] + dx / d * depth, M[1] + dy / d * depth)
    bow = bezier_pts(A, ctrl, B)
    for i in range(len(bow) - 1):
        glow_line(frame, bow[i], bow[i + 1], col, 3, blink)

    # tali A-C dan B-C
    glow_line(frame, A, C, col, 3, blink)
    glow_line(frame, B, C, col, 3, blink)

    # partikel mengalir dari garpu ke C
    n = 2 + int(pct * 0.08)
    pcol = tuple(int(c * blink) for c in col)
    partikel(frame, A, C, pcol, n, pct, time_s)
    partikel(frame, B, C, pcol, n, pct, time_s)

    # preview arah tembak
    proyeksi(frame, C, M, pct)

    # ujung garpu tajam
    for P, away in ((A, (A[0] - M[0], A[1] - M[1])), (B, (B[0] - M[0], B[1] - M[1]))):
        ad = math.hypot(away[0], away[1])
        if ad > 1:
            garpu(frame, P, (away[0] / ad, away[1] / ad), col)

    bola_energi(frame, C, pct, col)

    # label amunisi + stretch %
    label = f"<- {pct}% -> {filter_name}"
    font, scale, th = cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1
    (lw, lh), baseline = cv2.getTextSize(label, font, scale, th)
    h, w = frame.shape[:2]
    lx, ly = int(C[0]) + 10, int(C[1]) - 10
    if lx + lw > w - 5:
        lx = int(C[0]) - lw - 15
    if ly - lh - baseline < 0:
        ly = int(C[1]) + lh + 10
    cv2.rectangle(frame, (lx - 4, ly - lh - baseline - 2), (lx + lw + 4, ly + baseline), col, -1)
    cv2.putText(frame, label, (lx, ly), font, scale, (0, 0, 0), th, cv2.LINE_AA)


def draw_ammo_hud(frame, filter_name):
    """Pesan amunisi di bawah layar saat mode KETAPEL aktif."""
    h, w = frame.shape[:2]
    text = f"KETAPEL AMUNISI [{filter_name}] - LEPAS CUBITAN UNTUK TEMBAK!"
    font, scale = cv2.FONT_HERSHEY_SIMPLEX, 0.42
    (tw, _), _ = cv2.getTextSize(text, font, scale, 1)
    x = max((w - tw) // 2, 4)
    cv2.putText(frame, text, (x + 1, h - 28 + 1), font, scale, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(frame, text, (x, h - 28), font, scale, (50, 255, 50), 1, cv2.LINE_AA)