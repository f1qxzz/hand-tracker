"""Helper geometri & hitung jarak."""
import math


def jarak(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def get_bounds(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return {
        "left": min(xs), "top": min(ys),
        "right": max(xs), "bottom": max(ys),
    }


def smooth_polygon(prev, target, k=0.28):
    if target is None:
        return None
    if prev is None or len(prev) != len(target):
        return target
    return [
        (prev[i][0] + (t[0] - prev[i][0]) * k,
         prev[i][1] + (t[1] - prev[i][1]) * k)
        for i, t in enumerate(target)
    ]


def jarak_titik_segmen(p, a, b):
    ax, ay = a; bx, by = b
    vx, vy = bx - ax, by - ay
    l2 = vx * vx + vy * vy
    if l2 == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * vx + (p[1] - ay) * vy) / l2))
    return math.hypot(p[0] - (ax + t * vx), p[1] - (ay + t * vy))