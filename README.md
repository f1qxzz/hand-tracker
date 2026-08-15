# 🖐️ Cyber Frame Camera

Webcam app berbasis MediaPipe Hands: kontrol kamera/AR dengan gesture tangan real-time. Port Python dari `cyber-frame-camera`.

---

## ⚡ Setup & Run

```bash
pip install -r requirements.txt
python main.py
```

Butuh `hand_landmarker.task` (model MediaPipe) di root project.

---

## 🎮 Gesture & Kontrol

| Input | Aksi |
|-------|------|
| ✌️✌️ `L + L` | Satukan dua tangan = bingkai AR, tarik = buka |
| 🤏 `2 CUBIT` serentak | Ganti filter lensa |
| ✌️ + 🤏 `PEACE + CUBIT` | Mode **KETAPEL** — tarik = Y-shape, lepas cubit = tembak amunisi |
| ☝️ `TELUNJUK` (mode GAMBAR) | Menggambar |
| `G` | Ganti mode LENSA ↔ GAMBAR |
| `F` | Foto (simpan ke `foto/`) |
| `C` / `U` | Bersihkan / undo kanvas (mode GAMBAR) |
| `B` `V` `X` | Ganti warna pena / tebalin / tipisin |
| `S` | Reset posisi kanvas |
| `P` / `N` | Toggle / ganti filter manual |
| `ESC` / `Q` | Keluar |

---

## 📁 Struktur

```
hand_tracker/
├── main.py              # Entry: kamera loop, deteksi, keyboard
├── src/
│   ├── config.py        # Konstanta: model, filter, amunisi, warna
│   ├── geometry.py      # Jarak, bounds, smoothing polygon
│   ├── gesture.py       # Deteksi gesture tangan (L, peace, pinch, dll)
│   ├── filters.py       # 23 filter lensa + 10 layer amunisi ketapel
│   ├── ketapel.py       # Render ketapel: bezier, glow, partikel, bola energi
│   ├── lensa.py         # Mode LENSA: bingkai, auto-foto, deteksi ketapel
│   ├── gambar.py        # Mode GAMBAR: goresan, undo, geser, hapus
│   └── overlays.py      # HUD, ring, simpan foto
├── requirements.txt
└── README.md
```

---

## 🔧 Tips

- Pencahayaan cukup biar hand detection akurat.
- Jarak tangan ke kamera ideal ~40–80 cm.
- Ganti `DETECT_W/H` di `src/config.py` untuk trade-off FPS vs presisi.
