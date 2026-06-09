from flask import Blueprint, render_template, request, jsonify, send_file
from app.database import (
    get_filter_options, get_kabkota,
    pivot_provinsi, pivot_kabkota, pivot_sekolah,
    summary_cards, chart_by_bidang
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
    return jsonify(get_kabkota(provinsi if provinsi != 'semua' else None))


@bp.route('/api/summary')
def api_summary():
    filters = get_filters()
    return jsonify(summary_cards(filters))


@bp.route('/api/chart/bidang')
def api_chart_bidang():
    filters = get_filters()
    df = chart_by_bidang(filters)
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