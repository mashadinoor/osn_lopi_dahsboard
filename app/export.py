from flask import render_template
from weasyprint import HTML
from datetime import datetime
from pathlib import Path
import base64
import io


def get_logo_base64():
    logo_path = Path(__file__).parent / 'static' / 'img' / 'logo.png'
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None


def generate_pdf(filters, pivot_type, df_pivot, summary):
    kategori  = filters.get('kategori', 'Semua Kategori') or 'Semua Kategori'
    provinsi = filters.get('provinsi', 'Semua Provinsi') or 'Semua Provinsi'
    kab_kota = filters.get('kab_kota', '') or ''
    bidang   = filters.get('bidang', 'Semua Bidang') or 'Semua Bidang'
    tahun    = filters.get('tahun', 'Semua Tahun') or 'Semua Tahun'

    lokasi = kab_kota if kab_kota and kab_kota != 'semua' else provinsi
    judul  = f'Laporan Prestasi OSN {kategori} — {lokasi} {tahun}'

    pivot_labels = {
        'provinsi': 'Provinsi',
        'kabkota':  'Kab/Kota',
        'sekolah':  'Sekolah',
    }

    html_string = render_template(
        'export_pdf.html',
        judul=judul,
        timestamp=datetime.now().strftime('%d %B %Y, %H:%M WIB'),
        filters={
            'Tahun':     tahun,
            'Kategori':  kategori,
            'Provinsi':  provinsi,
            'Kab/Kota':  kab_kota or '—',
            'Bidang':    bidang,
        },
        pivot_type=pivot_type,
        pivot_label=pivot_labels.get(pivot_type, 'Wilayah'),
        rows=df_pivot.to_dict(orient='records'),
        columns=df_pivot.columns.tolist(),
        summary=summary,
        has_osnsf=df_pivot['lolos_osnsf'].notna().any() if 'lolos_osnsf' in df_pivot.columns else False,
        logo_b64=get_logo_base64(),
    )

    pdf_bytes = HTML(string=html_string, base_url=str(Path(__file__).parent)).write_pdf()
    return pdf_bytes, judul