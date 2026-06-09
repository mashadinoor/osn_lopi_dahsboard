# 📊 OSN LOPI Dashboard

Dashboard berbasis web untuk manajemen dan visualisasi data **LOPI Prestasi Indonesia** dalam rangka **Olimpiade Sains Nasional (OSN)**. Dibangun dengan Flask dan Python, aplikasi ini memudahkan pengelolaan data peserta, penilaian, serta ekspor laporan secara otomatis.

---

## ✨ Fitur Utama

- 📋 **Manajemen Data** — Kelola data peserta dan hasil penelitian secara terpusat
- 📈 **Visualisasi** — Tampilkan data dalam format yang mudah dibaca
- 📄 **Ekspor PDF** — Generate laporan PDF otomatis menggunakan WeasyPrint
- 📊 **Import Excel** — Baca dan proses data dari file `.xlsx` menggunakan Pandas & OpenPyXL
- 🌐 **Antarmuka Web** — Akses via browser, dibangun dengan Flask & Jinja2

---

## 🛠️ Tech Stack

| Komponen        | Teknologi      |
| --------------- | -------------- |
| Backend         | Python · Flask |
| Template Engine | Jinja2         |
| Data Processing | Pandas · NumPy |
| Excel Support   | OpenPyXL       |
| PDF Generator   | WeasyPrint     |
| Gambar          | Pillow         |

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/mashadinoor/osn_lopi_dahsboard.git
cd osn_lopi_dahsboard
```

### 2. Buat Virtual Environment (opsional tapi disarankan)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
source venv/Scripts/activate    # Windows
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi

```bash
python run.py
```

Aplikasi akan berjalan di `http://localhost:5000`

---

## 📁 Struktur Proyek

```
osn_lopi_dahsboard/
├── app/                  # Package utama aplikasi Flask
│   ├── __init__.py       # Factory function (create_app)
│   ├── routes/           # Definisi route/endpoint
│   ├── templates/        # Template HTML (Jinja2)
│   └── static/           # Aset statis (CSS, JS, gambar)
├── run.py                # Entry point aplikasi
├── requirements.txt      # Daftar dependensi
└── README.md
```

---

## ⚙️ Konfigurasi

Secara default, aplikasi berjalan dalam mode **debug** di `host 0.0.0.0` port `5000`. Konfigurasi ini bisa diubah langsung di `run.py`:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

> ⚠️ **Catatan:** Untuk deployment produksi, matikan mode debug dan gunakan WSGI server seperti Gunicorn.

---

## 📦 Dependensi Utama

```
Flask==3.1.3
pandas==2.3.3
openpyxl==3.1.5
weasyprint==69.0
numpy==2.2.6
Jinja2==3.1.6
Pillow==12.2.0
```

Lihat `requirements.txt` untuk daftar lengkap.

---

## 👤 Author

**mashadinoor** · [GitHub](https://github.com/mashadinoor)

---
> Dibuat dengan ❤️ untuk mendukung penyelenggaraan OSN LOPI yang lebih efisien.
