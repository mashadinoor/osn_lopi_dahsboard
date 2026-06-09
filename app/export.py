from flask import render_template
from weasyprint import HTML
from datetime import datetime
import io


def generate_pdf(filters, pivot_type, df_pivot, summary):
    """
    Render template HTML lalu convert ke PDF via WeasyPrint.
    Kembalikan bytes PDF.
    """
    # Label filter untuk judul dokumen
    kategori  = filters.get('kategori', 'Semua kategori') or 'Semua kategori'
    provinsi = filters.get('provinsi', 'Semua Provinsi') or 'Semua Provinsi'
    kab_kota = filters.get('kab_kota', '') or ''
    bidang   = filters.get('bidang', 'Semua Bidang') or 'Semua Bidang'
    tahun    = filters.get('tahun', 'Semua Tahun') or 'Semua Tahun'

    # Format judul: Laporan Prestasi OSN [kategori] — [Provinsi] [Tahun]
    lokasi = kab_kota if kab_kota and kab_kota != 'semua' else provinsi
    judul  = f'Laporan Prestasi OSN {kategori} — {lokasi} {tahun}'

    # Label kolom berdasarkan pivot type
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
            'Tahun':    tahun,
            'kategori':  kategori,
            'Provinsi': provinsi,
            'Kab/Kota': kab_kota or '—',
            'Bidang':   bidang,
        },
        pivot_type=pivot_type,
        pivot_label=pivot_labels.get(pivot_type, 'Wilayah'),
        rows=df_pivot.to_dict(orient='records'),
        columns=df_pivot.columns.tolist(),
        summary=summary,
        has_osnsf=df_pivot['lolos_osnsf'].notna().any() if 'lolos_osnsf' in df_pivot.columns else False,
    )

    pdf_bytes = HTML(string=html_string).write_pdf()
    return pdf_bytes, judul