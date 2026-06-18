# 📊 OSN LOPI Dashboard

Dashboard berbasis web untuk visualisasi dan ekspor data prestasi siswa **OSN (Olimpiade Sains Nasional)** — hasil pengumuman resmi Puspresnas — yang dikelola oleh **LOPI (Lembaga Olimpiade dan Prestasi Indonesia)**. Dibangun dengan Flask, aplikasi ini memudahkan tim marketing dan internal LOPI untuk memfilter, memvisualisasikan, dan mengekspor data pivot tanpa proses manual berulang.

---

## ✨ Fitur Utama

- 🔍 **Filter Multi-Select** — Filter berdasarkan tahun, kategori (SD/SMP/SMA), provinsi, kab/kota, dan bidang studi, dengan pencarian cepat
- 📊 **Pivot Table** — Top 5 data per provinsi, kab/kota, atau sekolah, dengan rincian jumlah peserta per tahapan OSN (OSP, SF, Final) dan medalis
- 🔻 **Funnel Chart** — Visualisasi corong tahapan OSN dari OSP hingga Medalis
- 🗺️ **Peta Interaktif** — Sebaran prestasi per provinsi se-Indonesia (Leaflet.js), warna berdasarkan jumlah lolos OSP
- 📄 **Ekspor PDF** — Generate laporan PDF terformat (judul, filter aktif, nama pengekspor, timestamp) menggunakan WeasyPrint
- 🗄️ **Database Cloud** — Data tersimpan di Supabase (PostgreSQL), bukan lagi file lokal — mendukung pertumbuhan data tahunan

---

## 🛠️ Tech Stack

| Komponen        | Teknologi                |
| --------------- | ------------------------ |
| Backend         | Python · Flask           |
| Database        | PostgreSQL (Supabase)    |
| Template Engine | Jinja2                   |
| Data Processing | Pandas                   |
| Peta Interaktif | Leaflet.js + GeoJSON     |
| Grafik          | Chart.js (custom funnel) |
| PDF Generator   | WeasyPrint               |
| Hosting         | Render                   |

---

## 🚀 Cara Menjalankan (Lokal)

### 1. Clone Repository

```bash
git clone https://github.com/mashadinoor/osn_lopi_dahsboard.git
cd osn_lopi_dahsboard
git checkout deploy-render
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install Dependensi

```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment Variable

Buat file `.env` di root project:

```
SUPABASE_URL=postgresql://postgres.xxxxx:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres
```

> Ambil connection string dari Supabase Dashboard → Project Settings → Database → Connection string → **Session Pooler**.

### 5. Jalankan Aplikasi

```bash
python run.py
```

Aplikasi berjalan di `http://localhost:5000`

---

## 📁 Struktur Proyek

```
osn_lopi_dahsboard/
├── app/
│   ├── __init__.py          # Factory function (create_app)
│   ├── database.py          # Koneksi & query Supabase (PostgreSQL)
│   ├── routes.py            # Definisi endpoint Flask
│   ├── export.py            # Generator PDF (WeasyPrint)
│   ├── templates/
│   │   ├── index.html       # Dashboard utama
│   │   └── export_pdf.html  # Template laporan PDF
│   └── static/
│       ├── img/logo.png
│       └── geojson/         # Peta provinsi Indonesia
├── run.py                   # Entry point lokal
├── requirements.txt
└── README.md
```

---

## 🗄️ Skema Database

Tabel `osn_siswa` di Supabase:

| Kolom          | Tipe    | Keterangan                                    |
| -------------- | ------- | --------------------------------------------- |
| `tahun`        | INTEGER | Tahun pelaksanaan OSN                         |
| `kategori`     | TEXT    | SD / SMP / SMA                                |
| `nama`         | TEXT    | Nama siswa                                    |
| `npsn`         | TEXT    | NPSN sekolah (tersedia mulai 2025)            |
| `sekolah`      | TEXT    | Nama sekolah                                  |
| `kab_kota`     | TEXT    | Kabupaten/Kota                                |
| `provinsi`     | TEXT    | Provinsi                                      |
| `bidang`       | TEXT    | Bidang studi (dinormalisasi)                  |
| `verified`     | INTEGER | 1 = peserta reguler, 0 = peserta undangan     |
| `lolos_osnp`   | INTEGER | Lolos ke OSN-Provinsi                         |
| `lolos_osnsf`  | INTEGER | Lolos ke OSN-Semi Final (null jika tidak ada) |
| `lolos_osnf`   | INTEGER | Lolos ke OSN-Final/Nasional                   |
| `jadi_medalis` | INTEGER | Mendapat medali                               |
| `medali`       | TEXT    | Emas / Perak / Perunggu / Honorable           |

> Semua baris merepresentasikan siswa yang telah **lolos OSN-Kabupaten**, karena data Puspresnas baru tersedia mulai dari tahap tersebut.

---

## ⚙️ Konfigurasi Produksi

Start command untuk Render (atau platform lain berbasis Gunicorn):

```
gunicorn app:app --timeout 120 --workers 1
```

Timeout diperpanjang untuk mengantisipasi ekspor PDF dengan data berjumlah ribuan baris (misal: pivot per sekolah tanpa filter wilayah).

---

## 📦 Dependensi Utama

```
Flask
pandas
psycopg2-binary
python-dotenv
weasyprint
gunicorn
```

Lihat `requirements.txt` untuk daftar lengkap dan versi pasti.

---

## 👤 Author

**mashadinoor** · [GitHub](https://github.com/mashadinoor)

---

> Dibuat dengan ❤️ untuk mendukung penyelenggaraan OSN LOPI yang lebih efisien.
