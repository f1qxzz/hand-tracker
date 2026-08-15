"""Engine filter gambar (lensa) + layer amunisi ketapel."""
import math

import cv2
import numpy as np

from .config import BAYER, AMUNISI_SCALE


def gray(bgr):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)


def _outer(bounds, frame):
    return (frame[max(0, int(bounds["top"])):int(bounds["bottom"]),
                  max(0, int(bounds["left"])):int(bounds["right"])])


def _inner(bounds, frame):
    w = int(bounds["right"]) - int(bounds["left"])
    h = int(bounds["bottom"]) - int(bounds["top"])
    return w, h


def filt_mono(frame):
    g = gray(frame)
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)


def filt_kontras(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 1.3)
    hsv[..., 2] = np.minimum(255, hsv[..., 2] * 1.05)
    bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return cv2.convertScaleAbs(bgr, alpha=1.6, beta=0)


def filt_film(frame, rng):
    g = cv2.cvtColor(cv2.convertScaleAbs(gray(frame), alpha=1.05), cv2.COLOR_GRAY2BGR)
    h, w = g.shape[:2]
    dots = rng.random((h, w)).astype(np.float32)
    mask = dots < 0.06
    g[mask] = np.minimum(255, g[mask].astype(np.int16) + 14).astype(np.uint8)
    return g


def filt_sobel(frame, background=True):
    g = gray(frame)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)
    edge = (mag > 55).astype(np.uint8) * 255
    if background:
        return cv2.cvtColor(edge, cv2.COLOR_GRAY2BGR)
    out = frame.copy()
    out[edge > 0] = 255
    return out


def filt_otsu(frame):
    g = gray(frame)
    _, thr = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)


def filt_dither(frame):
    g = gray(frame).astype(np.float32)
    h, w = g.shape
    bm = np.tile(BAYER, (h // 8 + 1, w // 8 + 1))[:h, :w]
    out = np.where(g > bm, 255, 0).astype(np.uint8)
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)


def filt_sketsa(frame):
    g = gray(frame)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)
    bg = np.where(g < 190, 220, 240)
    out = np.where(mag > 45, np.maximum(0, bg - 90), bg).astype(np.uint8)
    return cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)


def color_map(frame, lut):
    g = gray(frame)
    if lut == "jet":
        return cv2.applyColorMap(g, cv2.COLORMAP_JET)
    return cv2.applyColorMap(g, cv2.COLORMAP_HOT)


def filt_aqua(frame):
    g = gray(frame).astype(np.float32)
    r = np.clip(g * 1.1, 0, 255)
    cb = np.clip(g * 0.85 - 20, 0, 255)
    return np.stack([r, cb, g], axis=2).astype(np.uint8)


def filt_neon(frame, time_s):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] * 1.1 + 8) % 180
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 2.2)
    hsv[..., 2] = np.minimum(255, hsv[..., 2] * 1.15)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return cv2.convertScaleAbs(out, alpha=1.15, beta=-8)


def filt_pastel(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 0.65)
    hsv[..., 2] = np.minimum(255, hsv[..., 2] * 1.05 + 22)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def filt_vignet(frame):
    h, w = frame.shape[:2]
    g = gray(frame).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(np.sqrt(cx * cx + cy * cy), 1e-6)
    g = g * (1 - 0.5 * np.clip(d, 0, 1))
    return cv2.cvtColor(g.astype(np.uint8), cv2.COLOR_GRAY2BGR)


def filt_duo(frame):
    g = gray(frame).astype(np.float32)
    t = np.clip((g - 60) / 160.0, 0, 1)
    magenta = np.array([120, 0, 200], dtype=np.float32)
    cyan = np.array([235, 215, 0], dtype=np.float32)
    out = t[..., None] * cyan + (1 - t[..., None]) * magenta
    return out.astype(np.uint8)


def filt_cyber(frame, time_s, rng):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
    pulse = (math.sin(time_s * 0.009) + 1) / 2
    hsv[..., 0] = (hsv[..., 0] + 185 + pulse * 22) % 180
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 1.9)
    hsv[..., 2] = np.minimum(255, hsv[..., 2] * (0.92 + pulse * 0.10))
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    # screen overlay cyan/magenta
    h, w = out.shape[:2]
    cy = np.full_like(out, (255, 216, 0), dtype=np.uint8)   # BGR cyan-ish
    mg = np.full_like(out, (125, 22, 255), dtype=np.uint8)  # BGR magenta-ish
    sy = 1 - (1 - out / 255.0) * (1 - cy / 255.0)
    sm = 1 - (1 - out / 255.0) * (1 - mg * 0.22 / 255.0)
    out = (sy * 255).astype(np.uint8)
    mix = (out.astype(np.float32) * 0.78 + (sm * 255).astype(np.float32) * 0.22)
    out = np.clip(mix, 0, 255).astype(np.uint8)
    # glitch strips
    for i in range(3):
        y = int((time_s * (0.05 + i * 0.011) + i * 71) % max(1, h))
        sh = max(2, int(h * (0.012 + (i % 3) * 0.008)))
        if y < h:
            out[y:min(h, y + sh)] = out[y]
    return out


def filter_frame(f, kind, time_s, rng):
    """Terapkan filter ke seluruh frame (murni, tanpa clip)."""
    if kind == "cyber": return filt_cyber(f, time_s, rng)
    if kind == "mono": return filt_mono(f)
    if kind == "kontras": return filt_kontras(f)
    if kind == "film": return filt_film(f, rng)
    if kind in ("garis",): return filt_sobel(f, True)
    if kind == "tepi": return filt_sobel(f, False)
    if kind == "ambang": return filt_otsu(f)
    if kind == "dither": return filt_dither(f)
    if kind in ("negatif", "balik"): return cv2.bitwise_not(f)
    if kind == "termal": return color_map(f, "jet")
    if kind == "kedalaman": return color_map(f, "hot")
    if kind == "pixel":
        sk = max(2, f.shape[1] // 192)
        small = cv2.resize(f, (max(2, f.shape[1] // sk), max(2, f.shape[0] // sk)), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(small, (f.shape[1], f.shape[0]), interpolation=cv2.INTER_NEAREST)
    if kind == "pelangi":
        hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[..., 0] = (hsv[..., 0] + int((time_s * 60) % 360)) % 180
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    if kind == "sketsa": return filt_sketsa(f)
    if kind == "aqua": return filt_aqua(f)
    if kind == "neon": return filt_neon(f, time_s)
    if kind == "pastel": return filt_pastel(f)
    if kind == "vignet": return filt_vignet(f)
    if kind == "duo": return filt_duo(f)
    if kind == "sepia":
        m = np.array([[0.272, 0.534, 0.131],
                      [0.349, 0.686, 0.168],
                      [0.393, 0.769, 0.189]])
        sep = cv2.transform(f, m)
        if kind == "emas":
            sep = cv2.convertScaleAbs(sep, alpha=1.02)
            hsv = cv2.cvtColor(sep, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[..., 1] = np.minimum(255, hsv[..., 1] * 2.4)
            sep = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            gold = np.full_like(sep, (35, 155, 240), dtype=np.uint8)
            sep = (1 - (1 - sep / 255.0) * (1 - gold * 0.22 / 255.0)) * 255
            return sep.astype(np.uint8)
        return cv2.convertScaleAbs(sep, alpha=1.05)
    # rio
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] - 10) % 180
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 1.5)
    r = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    orange = np.full_like(r, (30, 110, 235), dtype=np.uint8)
    return (np.clip(1 - (1 - r / 255.0) * (1 - orange * 0.18 / 255.0), 0, 1) * 255).astype(np.uint8)


# ── Layer amunisi KETAPEL (filter seluruh layar) ─────────────────────────────
def am_cyber(f, time_s):
    h, w = f.shape[:2]
    g = gray(f)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)
    edge = (mag > 55).astype(np.uint8)
    out = np.clip(f.astype(np.float32) * 0.25, 0, 255).astype(np.uint8)
    k = np.ones((3, 3), np.uint8)
    outer = cv2.dilate(edge, k) & ~edge
    out[outer > 0] = (125, 22, 255)      # magenta elektrik
    out[edge > 0] = (255, 216, 0)        # cyan volt
    yy = np.arange(h) % 3 == 0  # scanline CRT
    out[yy] = (out[yy].astype(np.float32) * 0.7).astype(np.uint8)
    return out


def am_void(f, time_s):
    h, w = f.shape[:2]
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] * 0.6 + 135) % 180   # dorong ke ungu-biru
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 1.3)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(np.sqrt(cx * cx + cy * cy), 1e-6)
    v = np.clip(1 - 0.75 * d ** 2, 0.05, 1)[..., None]
    out = (out.astype(np.float32) * v).astype(np.uint8)
    rng = np.random.default_rng(int(time_s * 10))
    star = rng.random((h, w))
    pulse = 0.7 + 0.3 * np.sin(time_s * 3)
    out[star < 0.004 * pulse] = 255
    return out


def am_golden(f, time_s):
    m = np.array([[0.20, 0.55, 0.15], [0.25, 0.60, 0.15], [0.30, 0.65, 0.18]])
    out = cv2.transform(f, m)
    blur = cv2.GaussianBlur(out, (0, 0), 9)
    out = cv2.addWeighted(out, 0.75, blur, 0.25, 0)
    return cv2.convertScaleAbs(out, alpha=0.95, beta=8)


def am_blood(f, time_s):
    g = gray(f)
    red = np.clip(g * 1.5, 0, 255).astype(np.uint8)
    out = np.stack([(red * 0.35).astype(np.uint8), (red * 0.15).astype(np.uint8), red], axis=2)
    h, w = f.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    cx, cy = w / 2, h / 2
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / max(np.sqrt(cx * cx + cy * cy), 1e-6)
    ring = np.sin(d * 12 - time_s * 6) > 0.85
    out[ring] = np.maximum(out[ring].astype(np.int16), 40).astype(np.uint8)
    if int(time_s * 4) % 2 == 0 and (time_s % 0.5) < 0.08:
        out = np.clip(out.astype(np.float32) * 1.8, 0, 255).astype(np.uint8)
    return out


def am_frost(f, time_s):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 2] = np.minimum(255, hsv[..., 2] * 0.8 + 60)
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 0.5)
    hsv[..., 0] = (hsv[..., 0] * 0.5 + 105) % 180
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    rng = np.random.default_rng(int(time_s * 20))
    h, w = f.shape[:2]
    for _ in range(60):
        x0, y0 = int(rng.random() * w), int(rng.random() * h)
        ang = rng.random() * 6.28
        ln = 8 + rng.random() * 16
        cv2.line(out, (x0, y0), (int(x0 + ln * np.cos(ang)), int(y0 + ln * np.sin(ang))),
                 (245, 245, 250), 1, cv2.LINE_AA)
    return out


def am_negative(f, time_s):
    out = cv2.bitwise_not(f)
    sh = max(2, f.shape[1] // 160)
    out[..., 0] = np.roll(out[..., 0], sh)
    out[..., 2] = np.roll(out[..., 2], -sh)
    return out


def am_thermal(f, time_s):
    g = gray(f)
    out = cv2.applyColorMap(g, cv2.COLORMAP_INFERNO)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = cv2.magnitude(gx, gy)
    out[mag > 90] = 0
    h, w = f.shape[:2]
    cx, cy = w // 2, h // 2
    cv2.line(out, (cx - 20, cy), (cx + 20, cy), (0, 255, 0), 1)
    cv2.line(out, (cx, cy - 20), (cx, cy + 20), (0, 255, 0), 1)
    cv2.putText(out, "THR-7", (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)
    return out


def am_psychedelic(f, time_s):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 0] = (hsv[..., 0] + time_s * 35) % 180
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 1.8)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    h, w = f.shape[:2]
    for y in range(0, h, 4):
        sh = int(30 * np.sin(y * 0.02 + time_s * 2))
        if sh:
            out[y:y + 4] = np.roll(out[y:y + 4], sh, axis=1)
    return out


def am_paper(f, time_s):
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.minimum(255, hsv[..., 1] * 0.55)
    hsv[..., 2] = np.minimum(255, hsv[..., 2] * 0.7 + 80)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    g = gray(out)
    h, w = g.shape
    small = cv2.resize(g, (max(2, w // 24), max(2, h // 24)), interpolation=cv2.INTER_AREA)
    sm = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    mask = (sm < 128).astype(np.uint8)
    yy, xx = np.mgrid[0:h, 0:w]
    dots = (np.sin(xx / 24.0 * 6.28) ** 2) * (np.sin(yy / 24.0 * 6.28) ** 2) > 0.5
    ink = dots & (mask > 0)
    out = np.full_like(out, (200, 200, 235))
    out[ink] = (120, 120, 160)
    rng = np.random.default_rng(int(time_s * 30))
    gnoise = rng.random((h, w)) < 0.02
    out[gnoise] = np.minimum(out[gnoise].astype(np.int16) + 25, 255).astype(np.uint8)
    return out


def am_iron(f, time_s):
    g = cv2.convertScaleAbs(gray(f), alpha=1.35, beta=-25)
    out = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    dark = g < 70
    out[dark, 0] = np.clip(out[dark, 0] * 0.7, 0, 255)
    out[dark, 2] = np.clip(out[dark, 2] * 0.9, 0, 255)
    h, w = f.shape[:2]
    rng = np.random.default_rng(int(time_s * 30))
    gnoise = rng.random((h, w)) < 0.06
    out[gnoise] = (0, 0, 0)
    return out


def _apply_amunisi(f, kind, time_s):
    if kind == "cyber": return am_cyber(f, time_s)
    if kind == "void": return am_void(f, time_s)
    if kind == "golden": return am_golden(f, time_s)
    if kind == "blood": return am_blood(f, time_s)
    if kind == "frost": return am_frost(f, time_s)
    if kind == "negative": return am_negative(f, time_s)
    if kind == "thermal": return am_thermal(f, time_s)
    if kind == "psychedelic": return am_psychedelic(f, time_s)
    if kind == "paper": return am_paper(f, time_s)
    if kind == "iron": return am_iron(f, time_s)
    return f


def filter_amunisi(f, kind, time_s):
    h, w = f.shape[:2]
    small = cv2.resize(f, (int(w * AMUNISI_SCALE), int(h * AMUNISI_SCALE)), interpolation=cv2.INTER_AREA)
    out = _apply_amunisi(small, kind, time_s)
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_LINEAR)