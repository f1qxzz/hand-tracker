"""Konstanta & konfigurasi global app."""
import os

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.path.join(BASE, "hand_landmarker.task")
FOTO_DIR = os.path.join(BASE, "foto")
os.makedirs(FOTO_DIR, exist_ok=True)

# ── Konfigurasi (sama seperti core.js) ─────────────────────────────────────
DEBUG_PINCH = True       # HUD debug gesture tiap tangan (ubah False kalau sudah jalan)
TAHAN_FOTO = 3.0         # detik tangan diam untuk auto-foto
MULAI_BUTUH = 2          # frame beruntun untuk mulai gambar
HENTI_BUTUH = 8          # frame beruntun untuk stop gambar (lebih toleran biar garis kontinu)
MAX_HAND = 2
AMBANG_FOTO = 0.35       # min detection / presence / tracking confidence
DETECT_W = 480           # frame deteksi (dikcilin biar TFLite cepat -> FPS naik)
DETECT_H = 270
TAHAN_QUAD_HILANG = 0.45  # detik quad ditahan saat tangan sesaat tidak terdeteksi

# ── Topologi tulang (hand.js) ───────────────────────────────────────────────
HAND_CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8],
    [5, 9], [9, 10], [10, 11], [11, 12], [9, 13], [13, 14], [14, 15],
    [15, 16], [13, 17], [17, 18], [18, 19], [19, 20], [0, 17],
]

# ── Daftar filter (lensa.js) ────────────────────────────────────────────────
LENSA = [
    ("CYBER", "cyber"), ("MONO", "mono"), ("KONTRAS", "kontras"),
    ("FILM", "film"), ("GARIS", "garis"), ("AMBANG", "ambang"),
    ("DITHER", "dither"), ("NEGATIF", "negatif"), ("TEPI", "tepi"),
    ("TERMAL", "termal"), ("KEDALAMAN", "kedalaman"), ("BALIK", "balik"),
    ("PIXEL", "pixel"), ("PELANGI", "pelangi"), ("SKETSA", "sketsa"),
    ("SEPIA", "sepia"), ("EMAS", "emas"), ("RIO", "rio"),
    ("AQUA", "aqua"), ("NEON", "neon"), ("PASTEL", "pastel"),
    ("VIGNET", "vignet"), ("DUO", "duo"),
]

# ── Amunisi KETAPEL (layer filter seluruh layar) ─────────────────────────────
AMUNISI = [
    ("CYBER_NEON", "cyber"), ("VOID_PULSE", "void"), ("GOLDEN_HOUR", "golden"),
    ("BLOOD_RUSH", "blood"), ("FROSTBITE", "frost"), ("NEGATIVE_REVERSE", "negative"),
    ("THERMAL_VISION", "thermal"), ("PSYCHEDELIC", "psychedelic"),
    ("PAPER_DAWN", "paper"), ("IRON_GRIT", "iron"),
]
AMUNISI_SCALE = 0.5      # layer amunisi di-render di setengah resolusi biar fps gak drop
FLASH_FRAMES = 4         # durasi flash saat ketapel ditembaki
SLIDE_FRAMES = 6         # frame slide-in layer amunisi setelah fire

# ── Mode GAMBAR ─────────────────────────────────────────────────────────────
PENA = [(230, 180, 120), (0, 235, 255), (255, 0, 200), (180, 180, 0)]  # BGR
HISTORI_MAKS = 20

# ── Bayer matrix 8x8 (filters.js) ───────────────────────────────────────────
BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]
BAYER = (np.array(BAYER8, dtype=np.float32) / 64.0 * 255.0)