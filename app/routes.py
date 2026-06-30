from flask import Blueprint, render_template, request, jsonify, send_file
from app.database import (
    get_filter_options, get_kabkota,
    pivot_provinsi, pivot_kabkota, pivot_sekolah, pivot_by_bidang,
    summary_cards, funnel_data, map_data, map_data_kabkota
)
from app.export import generate_pdf, generate_pdf_bidang
import io
import time

bp = Blueprint('main', __name__)


def get_filters():
    return {
        'tahun':    request.args.get('tahun', 'semua'),
        'kategori': request.args.get('kategori', 'semua'),
        'provinsi': request.args.get('provinsi', 'semua'),
        'kab_kota': request.args.get('kab_kota', 'semua'),
        'bidang':   request.args.get('bidang', 'semua'),
    }


@bp.route('/')
def index():
    opts = get_filter_options()
    return render_template('index.html', opts=opts)


@bp.route('/api/kabkota')
def api_kabkota():
    provinsi = request.args.get('provinsi')
    if provinsi and provinsi != 'semua':
        provs = [p for p in provinsi.split(',') if p]
        results = []
        for p in provs:
            results.extend(get_kabkota(p))
        seen = set()
        unique = []
        for k in results:
            if k not in seen:
                seen.add(k)
                unique.append(k)
        return jsonify(sorted(unique))
    return jsonify(get_kabkota(None))


@bp.route('/api/summary')
def api_summary():
    return jsonify(summary_cards(get_filters()))


@bp.route('/api/funnel')
def api_funnel():
    return jsonify(funnel_data(get_filters()))


@bp.route('/api/map')
def api_map():
    from app.database import map_data_kabkota
    df = map_data_kabkota(get_filters())
    return jsonify(df.to_dict(orient='records'))

@bp.route('/api/map/kabkota')
def api_map_kabkota():
    from app.database import map_data_kabkota
    df = map_data_kabkota(get_filters())
    return jsonify(df.to_dict(orient='records'))


@bp.route('/api/pivot/<pivot_type>')
def api_pivot(pivot_type):
    filters = get_filters()
    if pivot_type == 'provinsi':
        df = pivot_provinsi(filters)
    elif pivot_type == 'kabkota':
        df = pivot_kabkota(filters)
    elif pivot_type == 'sekolah':
        df = pivot_sekolah(filters)
    else:
        return jsonify({'error': 'pivot type tidak valid'}), 400

    df = df.head(5)

    return jsonify({
        'columns': df.columns.tolist(),
        'rows': df.to_dict(orient='records'),
    })


@bp.route('/export/pdf/<pivot_type>')
def export_pdf(pivot_type):
    t0 = time.time()

    exported_by = request.args.get('nama', '—')
    export_mode = request.args.get('export_mode', 'tahapan')  # 'tahapan' atau 'bidang'
    tahapan_col = request.args.get('tahapan_col', 'lolos_osnp')
    filters = get_filters()

    # ── MODE B: Bidang sebagai kolom ──────────────────────────
    if export_mode == 'bidang':
        if pivot_type not in ('provinsi', 'kabkota', 'sekolah'):
            return 'pivot type tidak valid', 400

        bidang_data = pivot_by_bidang(filters, pivot_type, tahapan_col)
        t1 = time.time()
        print(f'[TIMING] Query pivot bidang: {t1-t0:.2f}s | {len(bidang_data["rows"])} baris')

        pdf_bytes, filename = generate_pdf_bidang(filters, pivot_type, bidang_data, exported_by, tahapan_col)
        t2 = time.time()
        print(f'[TIMING] Generate PDF: {t2-t1:.2f}s | TOTAL: {t2-t0:.2f}s')

        filename = filename.replace(' ', '_').replace('/', '-') + '.pdf'
        return send_file(
            io.BytesIO(pdf_bytes), mimetype='application/pdf',
            as_attachment=True, download_name=filename,
        )

    # ── MODE A: Tahapan OSN sebagai kolom (tabel biasa untuk semua pivot) ──
    if pivot_type == 'provinsi':
        df = pivot_provinsi(filters)
    elif pivot_type == 'kabkota':
        df = pivot_kabkota(filters)
    elif pivot_type == 'sekolah':
        df = pivot_sekolah(filters)
    else:
        return 'pivot type tidak valid', 400

    t1 = time.time()
    print(f'[TIMING] Query pivot: {t1-t0:.2f}s | {len(df)} baris')

    summary = summary_cards(filters)
    t2 = time.time()

    pdf_bytes, filename = generate_pdf(filters, pivot_type, df, summary, exported_by)
    t3 = time.time()
    print(f'[TIMING] Generate PDF: {t3-t2:.2f}s | TOTAL: {t3-t0:.2f}s')

    filename = filename.replace(' ', '_').replace('/', '-') + '.pdf'

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )