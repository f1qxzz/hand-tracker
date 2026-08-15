# 🖐️ CYBER FRAME CAMERA

<div align="center">

**Kamera AR real-time yang dikendalikan murni dengan gesture tangan.**

Tangan lo jadi *remote control* — bikin bingkai cyber, tembak filter dengan ketapel, sampe gambar digital di udara. Tanpa mouse, tanpa keyboard (kecuali mau).

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-1F9E37?style=for-the-badge&logo=mediapipe&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)

</div>

---

## ⚡ THE IDEA

Kamera lo bukan cuma *recorder*. Ia jadi **kanvas + konsol game + studio efek** sekaligus. Semua di-control dari dua tangan di depan webcam.

| Mode | Cara Pakai | Hasil |
|------|-----------|-------|
| 🪟 **FRAME** | Bentuk `L` di dua tangan, satukan, lalu tarik | Bingkai AR cyber dengan filter di dalamnya |
| 💥 **KETAPEL** | Satu tangan `✌️ peace` + tangan lain `🤏 cubit`, tarik & lepas | "Menembak" layer filter yang menutupi seluruh layar |
| 🎨 **GAMBAR** | Telunjuk menunjuk → coret-coret di udara | Gambar digital live di atas video |

---

## 🎮 GESTURE & KONTROL

```
╔═══════════════════════════════════════════════════════════════╗
║  ✌️✌️  L + L           = Buka bingkai AR (tarik = perbesar)      ║
║  🤏🤏  2 CUBIT         = Ganti filter lensa                      ║
║  ✌️ + 🤏 PEACE+CUBIT  = Mode KETAPEL: tarik → LEPAS = TEMBAK     ║
║  ☝️    TELUNJUK        = Gambar (mode GAMBAR)                    ║
║  ✊    KEPAL           = Geser semua goresan                     ║
╚═══════════════════════════════════════════════════════════════╝
```

### ⌨️ Keyboard (opsional)

| Key | Aksi |
|-----|------|
| `G` | Ganti mode **LENSA ↔ GAMBAR** |
| `F` | Foto → `foto/` |
| `C` / `U` | Clear / Undo kanvas |
| `B` / `V` / `X` | Warna pena / tebal / tipis |
| `S` | Reset posisi kanvas |
| `P` / `N` | Toggle / ganti filter manual |
| `ESC` / `Q` | Keluar |

---

## 💥 FITUR KETAPEL

Ini bintang utamanya. Peace + cubit = ketapel beneran:

- 🏹 **Busur bezier responsif** — makin ditarik, busur makin tegang & lurus. Fisika ketapel asli.
- ✨ **Glow 3 lapis** — setiap garis digambar dengan halo gelap + inti neon + core putih-panas.
- ⚡ **Partikel energi** — titik-titik mengalir dari garpu ke titik tarik, makin deras makin ditarik.
- 🔴 **Color shift** — hijau tenang → kuning → oranye → merah saat stretch 70%+ (peringatan batas maksimal).
- 🎯 **Garis proyeksi** — preview ke mana amunisi bakal terbang.
- 💥 **Fire effect** — flash putih + shockwave ring + slide-in layer filter baru.

### 10 Amunisi

`CYBER_NEON` · `VOID_PULSE` · `GOLDEN_HOUR` · `BLOOD_RUSH` · `FROSTBITE` · `NEGATIVE_REVERSE` · `THERMAL_VISION` · `PSYCHEDELIC` · `PAPER_DAWN` · `IRON_GRIT`

---

## 🎨 23 FILTER LENSA

`CYBER` · `MONO` · `KONTRAS` · `FILM` · `GARIS` · `AMBANG` · `DITHER` · `NEGATIF` · `TEPI` · `TERMAL` · `KEDALAMAN` · `BALIK` · `PIXEL` · `PELANGI` · `SKETSA` · `SEPIA` · `EMAS` · `RIO` · `AQUA` · `NEON` · `PASTEL` · `VIGNET` · `DUO`

---

## 📁 STRUKTUR PROYEK

```
hand_tracker/
├── main.py              # 🚀 Entry: loop kamera, deteksi, keyboard
├── src/
│   ├── config.py        # ⚙️  Konstanta: model, filter, amunisi, warna
│   ├── geometry.py      # 📐 Jarak, bounds, smoothing polygon
│   ├── gesture.py       # 🖐️  Deteksi gesture (L, peace, pinch, kepal…)
│   ├── filters.py       # 🎨 23 filter lensa + 10 layer amunisi ketapel
│   ├── ketapel.py       # 💥 Render ketapel: bezier, glow, partikel, bola
│   ├── lensa.py         # 🪟 Mode LENSA: bingkai AR, auto-foto, ketapel
│   ├── gambar.py        # 🎨 Mode GAMBAR: goresan, undo, geser, hapus
│   └── overlays.py      # 📺 HUD, ring progress, simpan foto
├── requirements.txt
└── README.md
```

---

## ⚡ SETUP

```bash
# 1. Clone & masuk
git clone https://github.com/f1qxzz/hand-tracker
cd hand-tracker

# 2. Install dependency
pip install -r requirements.txt

# 3. Siapkan model MediaPipe (hand_landmarker.task) di root project

# 4. Jalan!
python main.py
```

> 💡 Model `hand_landmarker.task` bisa didownload dari [MediaPipe Models](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker#models).

---

## 🔧 TIPS

- 💡 **Cahaya cukup** — akurasi hand detection naik drastis.
- 📏 **Jarak 40–80 cm** dari kamera adalah sweet spot.
- 🎛️ **FPS vs presisi** — ubah `DETECT_W/H` di `src/config.py`. Kecilin = FPS naik.
- 🤏 **Sensitifitas pinch** — ubah threshold di `src/gesture.py`.

---

<div align="center">

Made with 🖐️ + 🐍 + too much kafein

</div>
