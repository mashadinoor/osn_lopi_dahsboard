from flask import Blueprint, render_template, request, jsonify, send_file
from app.database import (
    get_filter_options, get_kabkota,
    pivot_provinsi, pivot_kabkota, pivot_sekolah,
    summary_cards, funnel_data, map_data
)
from app.export import generate_pdf
import io

bp = Blueprint('main', __name__)


def get_filters():
    return {
        'tahun':    request.args.get('tahun', 'semua'),
        'kategori':  request.args.get('kategori', 'semua'),
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
    df = map_data(get_filters())
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

    # Top 5
    df = df.head(5)

    return jsonify({
        'columns': df.columns.tolist(),
        'rows': df.to_dict(orient='records'),
    })


@bp.route('/export/pdf/<pivot_type>')
def export_pdf(pivot_type):
    filters = get_filters()
    if pivot_type == 'provinsi':
        df = pivot_provinsi(filters)
    elif pivot_type == 'kabkota':
        df = pivot_kabkota(filters)
    elif pivot_type == 'sekolah':
        df = pivot_sekolah(filters)
    else:
        return 'pivot type tidak valid', 400

    summary = summary_cards(filters)
    pdf_bytes, judul = generate_pdf(filters, pivot_type, df, summary)
    filename = judul.replace(' ', '_').replace('—', '-') + '.pdf'

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename,
    )