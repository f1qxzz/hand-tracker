<div align="center">

```
  ██████╗██╗   ██╗██████╗ ███████╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗
 ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝
 ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    █████╗  ██████╔╝███████║██╔████╔██║█████╗
 ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝
 ╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗
  ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
```

**CAMERA · AR · GESTURE**

Dua tangan lo bukan buat berdoa — ini *remote control* kamera AR.
Bingkai cyber, filter 23 gaya, dan ketapel yang menembak warna.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-4CAF50?style=for-the-badge&logo=mediapipe&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

</div>

---

## 🕹️ TIGA MODE — SATU KAMERA

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                    │
│   ✌️✌️  L + L      🪟 FRAME      tarik & buka bingkai AR           │
│   ✌️ + 🤏         💥 KETAPEL    tarik → lepas → tembak filter      │
│   ☝️              🎨 GAMBAR     telunjuk = kuas, udara = kanvas    │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### ⌨️ Keyboard

| Key | Aksi |
|-----|------|
| `G` | LENSA ↔ GAMBAR |
| `F` | Foto → `foto/` |
| `C` `U` | Clear / Undo |
| `B` `V` `X` | Warna / tebal / tipis |
| `S` `P` `N` | Reset / toggle / ganti filter |
| `ESC` | Keluar |

---

## 💥 KETAPEL — THE MAIN EVENT

```
   peace 🖐️✌️ + cubit 🤏
        │
        │  TARIK → busur menekuk, bola energi membesar,
        │          warna naik: 🟢 → 🟡 → 🟠 → 🔴
        ▼
     LEPAS → B A N G !  💥 flash + shockwave + amunisi menutup layar
```

| Fitur | Detail |
|-------|--------|
| 🏹 Busur bezier | Melengkung menjauhi titik tarik; makin kencang makin lurus |
| ✨ Glow 3 lapis | Halo gelap → inti neon → core putih panas |
| ⚡ Partikel energi | Mengalir dari garpu ke tarikan, akselerasi di ujung |
| 🔴 Color shift | Hijau→kuning→oranye→merah, berkedip di 70%+ |
| 🎯 Proyeksi | Garis putus-putus preview arah tembakan |
| 💥 Fire FX | Flash + shockwave ring + slide-in filter baru |

**10 amunisi:** `CYBER_NEON` · `VOID_PULSE` · `GOLDEN_HOUR` · `BLOOD_RUSH` · `FROSTBITE` · `NEGATIVE_REVERSE` · `THERMAL_VISION` · `PSYCHEDELIC` · `PAPER_DAWN` · `IRON_GRIT`

---

## 🎨 23 FILTER LENSA

```
CYBER    MONO     KONTRAS  FILM     GARIS    AMBANG   DITHER
NEGATIF  TEPI     TERMAL   KEDALAMAN BALIK   PIXEL    PELANGI
SKETSA   SEPIA    EMAS     RIO      AQUA     NEON     PASTEL
VIGNET   DUO
```

---

## 📁 STRUKTUR

```
hand_tracker/
├── main.py            🚀 entry: kamera loop + keyboard
├── src/
│   ├── config.py      ⚙️  konstanta & daftar filter/amunisi
│   ├── geometry.py    📐 jarak, bounds, smoothing
│   ├── gesture.py     🖐️  deteksi gesture tangan
│   ├── filters.py     🎨 23 filter + 10 amunisi
│   ├── ketapel.py     💥 render ketapel (bezier, glow, partikel)
│   ├── lensa.py       🪟 mode frame AR + auto-foto + ketapel
│   ├── gambar.py      🎨 mode gambar (goresan, undo, geser)
│   └── overlays.py    📺 HUD + simpan foto
└── requirements.txt
```

---

## ⚡ JALANKAN

```bash
git clone https://github.com/f1qxzz/hand-tracker
cd hand-tracker
pip install -r requirements.txt   # + hand_landmarker.task di root
python main.py
```

> Model MediaPipe: [developers.google.com/mediapipe/.../hand_landmarker](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models)

---

## 🔧 TUNING

| Ingin | Ubah di `src/config.py` |
|-------|------------------------|
| 🚀 FPS lebih tinggi | Kecilkan `DETECT_W/H` |
| 📡 Deteksi lebih stabil | Naikkan `TAHAN_QUAD_HILANG` |
| 🔥 Ketapel lebih gampang nembak | Turunkan threshold pinch di `src/gesture.py` |

---

<div align="center">

**MADE WITH 🖐️ + 🐍 + CAFEIN** · [f1qxzz/hand-tracker](https://github.com/f1qxzz/hand-tracker)

</div>
