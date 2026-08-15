"""Deteksi gesture tangan dari landmark normalised."""
from .geometry import jarak


def jari_terbuka(hand):
    """hand = list 21 x (x,y) normalised (flipped-x belum)."""
    w = hand[0]
    ref = hand[17]
    return [
        jarak(hand[4], ref) > jarak(hand[2], ref) * 1.15,
        jarak(hand[8], w) > jarak(hand[6], w) * 1.12,
        jarak(hand[12], w) > jarak(hand[10], w) * 1.12,
        jarak(hand[16], w) > jarak(hand[14], w) * 1.12,
        jarak(hand[20], w) > jarak(hand[18], w) * 1.12,
    ]


def is_l(f): return f[0] and f[1] and not f[2] and not f[3] and not f[4]
def is_tunjuk(f): return f[1] and not f[2] and not f[3] and not f[4]
def is_peace(f): return f[1] and f[2] and not f[3] and not f[4]
def is_kepal(f): return not f[1] and not f[2] and not f[3] and not f[4]


def is_pinch(hand):
    # ukuran telapak stabil: wrist -> middle MCP (9). Lebih reliable drpd wrist->pinky(17)
    return jarak(hand[4], hand[8]) / max(jarak(hand[0], hand[9]), 1e-6) < 0.45


def nama_gesture(f):
    if is_peace(f):
        return "PEACE"
    if is_kepal(f):
        return "KEPAL"
    if is_l(f):
        return "L"
    if f[1] and not f[2] and not f[3] and not f[4]:
        return "TUNJUK"
    return "?"


def build_info(hands, W, H):
    """hands: list(list(21 (x,y))) normalised -> [(hand, fingers, px)].
    px = flipped x, pakai (1-x)*W biar konsisten dgn video mirror."""
    out = []
    for hand in hands:
        f = jari_terbuka(hand)
        px = [[(1 - lm[0]) * W, lm[1] * H] for lm in hand]
        out.append((hand, f, px))
    return out