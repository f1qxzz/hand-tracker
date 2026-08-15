"""Mode GAMBAR: menggambar dengan telunjuk, hapus/geser dengan gesture lain."""
import copy
import math

import cv2
import numpy as np

from .config import PENA, HAND_CONNECTIONS, MULAI_BUTUH, HENTI_BUTUH, HISTORI_MAKS
from .gesture import is_kepal, is_pinch, is_peace
from .geometry import jarak_titik_segmen
from .overlays import draw_hud

idx_pena = 0
ketebalan = 6
histori = []
menggambar = False
beruntun_ya = 0
beruntun_tidak = 0
goresan = 0
pena_halus = None
pena_akhir = None
seret = [0, 0]
seret_sebelum = None
# goresan = list of dict: {"pts":[(x,y)...], "warna":tuple, "tebal":int, "ox":float, "oy":float}
goresan_list = []
goresan_aktif = None   # index goresan yang lagi digambar
geser_idx = None       # index goresan yang disentuh cubit (buat digeser)
geser_prev = None      # posisi cubit sebelumnya
geser_halus = None     # posisi cubit yang di-EMA biar gesernya mulus


def reset_gambar_state():
    global pena_halus, pena_akhir, menggambar, beruntun_ya, beruntun_tidak
    global goresan_aktif, geser_idx, geser_prev, geser_halus
    pena_halus = None
    pena_akhir = None
    menggambar = False
    beruntun_ya = beruntun_tidak = 0
    goresan_aktif = None
    geser_idx = None
    geser_prev = None
    geser_halus = None


def clear_kanvas():
    global goresan_list, histori, goresan
    goresan_list = []
    histori = []
    goresan = 0


def undo_gambar(W, H):
    global goresan_list
    if not histori:
        return
    goresan_list = histori.pop()


def goresan_terdekat(p, ambang=40.0):
    """index goresan paling dekat dengan titik p, atau None."""
    best = None
    bd = ambang
    for i, g in enumerate(goresan_list):
        for j in range(len(g["pts"]) - 1):
            a = (g["pts"][j][0] + g["ox"], g["pts"][j][1] + g["oy"])
            b = (g["pts"][j + 1][0] + g["ox"], g["pts"][j + 1][1] + g["oy"])
            d = jarak_titik_segmen(p, a, b)
            if d < bd:
                bd = d
                best = i
    return best


def render_gambar(frame, info, time_s, W, H):
    global idx_pena, ketebalan, menggambar, beruntun_ya, beruntun_tidak
    global goresan, pena_halus, pena_akhir, seret, seret_sebelum, histori
    global goresan_list, goresan_aktif, geser_idx, geser_prev, geser_halus

    # video digelapkan
    canvas_out = (frame.astype(np.float32) * 0.45).astype(np.uint8)

    status = "SIAP"
    ujung = None
    gambar_ok = False

    if info:
        hand, f, px = info[0]
        ujung = px[8]

        if is_kepal(f):
            # KEPAL = geser SEMUA goresan
            geser_idx = None
            geser_prev = None
            p = px[9]
            if seret_sebelum is not None:
                seret[0] += max(-30, min(30, p[0] - seret_sebelum[0]))
                seret[1] += max(-30, min(30, p[1] - seret_sebelum[1]))
                seret[0] = max(-300, min(300, seret[0]))
                seret[1] = max(-300, min(300, seret[1]))
            seret_sebelum = p
            status = "SERET"
        elif is_pinch(hand):
            # CUBIT = geser goresan yang DISENTUH aja
            seret_sebelum = None
            if geser_prev is None:
                geser_idx = goresan_terdekat(ujung, ambang=50.0)
                geser_prev = [ujung[0], ujung[1]]
                geser_halus = [ujung[0], ujung[1]]
            else:
                geser_halus[0] += (ujung[0] - geser_halus[0]) * 0.35
                geser_halus[1] += (ujung[1] - geser_halus[1]) * 0.35
                if geser_idx is not None:
                    g = goresan_list[geser_idx]
                    g["ox"] += geser_halus[0] - geser_prev[0]
                    g["oy"] += geser_halus[1] - geser_prev[1]
                geser_prev = [geser_halus[0], geser_halus[1]]
            status = "GESER" if geser_idx is not None else "GESER?"
        elif is_peace(f):
            # PEACE = hapus goresan terdekat
            geser_idx = None
            geser_prev = None
            seret_sebelum = None
            idx = goresan_terdekat(ujung, ambang=40.0)
            if idx is not None:
                if goresan_aktif is not None and idx <= goresan_aktif:
                    goresan_aktif = None
                    menggambar = False
                if geser_idx == idx:
                    geser_idx = None
                del goresan_list[idx]
                status = "HAPUS"
            else:
                status = "HAPUS?"
        else:
            # TELUNJUK = gambar
            geser_idx = None
            geser_prev = None
            seret_sebelum = None
            gambar_ok = True
            status = "GAMBAR"

        if gambar_ok:
            beruntun_ya += 1; beruntun_tidak = 0
        else:
            beruntun_tidak += 1; beruntun_ya = 0

        # mulai goresan baru (snapshot utk undo) / stop
        if not menggambar and beruntun_ya >= MULAI_BUTUH:
            histori.append(copy.deepcopy(goresan_list))
            if len(histori) > HISTORI_MAKS:
                histori.pop(0)
            goresan_list.append({"pts": [], "warna": PENA[idx_pena], "tebal": ketebalan,
                                 "ox": 0.0, "oy": 0.0})
            goresan_aktif = len(goresan_list) - 1
            menggambar = True
            pena_halus = None
            pena_akhir = None
        elif menggambar and beruntun_tidak >= HENTI_BUTUH:
            menggambar = False
            goresan_aktif = None
            pena_akhir = pena_halus = None

        # tambah titik ke goresan aktif
        if menggambar and goresan_aktif is not None and ujung is not None:
            p = [ujung[0], ujung[1]]
            if pena_halus is None:
                pena_halus = [p[0], p[1]]
            else:
                vx = p[0] - pena_halus[0]
                vy = p[1] - pena_halus[1]
                spd = math.hypot(vx, vy)
                alfa = 0.9 if spd > 40 else (0.7 if spd > 12 else 0.5)
                pena_halus = [pena_halus[0] + alfa * vx, pena_halus[1] + alfa * vy]
            titik = [pena_halus[0], pena_halus[1]]
            g = goresan_list[goresan_aktif]
            if not g["pts"] or abs(titik[0] - g["pts"][-1][0]) + abs(titik[1] - g["pts"][-1][1]) >= 4:
                g["pts"].append((titik[0], titik[1]))
                goresan += 1

        # skeleton
        for c in HAND_CONNECTIONS:
            cv2.line(canvas_out, (int(px[c[0]][0]), int(px[c[0]][1])),
                     (int(px[c[1]][0]), int(px[c[1]][1])), (90, 80, 80), 1, cv2.LINE_AA)
        for i in (4, 8, 12, 16, 20):
            cv2.circle(canvas_out, (int(px[i][0]), int(px[i][1])), 4, (235, 60, 235), -1)

    # gambar semua goresan + offset global
    for g in goresan_list:
        for j in range(len(g["pts"]) - 1):
            a = (int(g["pts"][j][0] + g["ox"] + seret[0]),
                 int(g["pts"][j][1] + g["oy"] + seret[1]))
            b = (int(g["pts"][j + 1][0] + g["ox"] + seret[0]),
                 int(g["pts"][j + 1][1] + g["oy"] + seret[1]))
            cv2.line(canvas_out, a, b, g["warna"], g["tebal"], cv2.LINE_AA)
    # highlight goresan yang lagi digeser
    if geser_idx is not None and 0 <= geser_idx < len(goresan_list):
        g = goresan_list[geser_idx]
        for j in range(len(g["pts"]) - 1):
            a = (int(g["pts"][j][0] + g["ox"] + seret[0]),
                 int(g["pts"][j][1] + g["oy"] + seret[1]))
            b = (int(g["pts"][j + 1][0] + g["ox"] + seret[0]),
                 int(g["pts"][j + 1][1] + g["oy"] + seret[1]))
            cv2.line(canvas_out, a, b, (255, 255, 255), g["tebal"] + 2, cv2.LINE_AA)

    draw_hud(canvas_out, f"{status}  GORESAN {goresan}", 22, H - 45, 0.7, (111, 112, 120))
    draw_hud(canvas_out, "TELUNJUK=GAMBAR PEACE=HAPUS CUBIT=GESER KEPAL=GESER SEMUA G=KELUAR B=PENA V/X=TEBAL",
             22, H - 20, 0.55, (111, 112, 120))
    # kotak indikator pena
    color = PENA[idx_pena]
    cv2.rectangle(canvas_out, (W - 90, H - 100), (W - 10, H - 60), color, 2)
    cv2.circle(canvas_out, (W - 50, H - 80), ketebalan, color, -1)

    return canvas_out