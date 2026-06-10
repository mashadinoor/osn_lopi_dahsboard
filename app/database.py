import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'osn_dashboard.db'


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Filter options ──────────────────────────────────────────────

def get_filter_options():
    conn = get_conn()
    opts = {}
    opts['tahun']   = [r[0] for r in conn.execute('SELECT DISTINCT tahun   FROM osn_siswa ORDER BY tahun').fetchall()]
    opts['kategori'] = [r[0] for r in conn.execute('SELECT DISTINCT kategori FROM osn_siswa ORDER BY kategori').fetchall()]
    opts['provinsi']= [r[0] for r in conn.execute('SELECT DISTINCT provinsi FROM osn_siswa ORDER BY provinsi').fetchall()]
    opts['bidang']  = [r[0] for r in conn.execute('SELECT DISTINCT bidang  FROM osn_siswa ORDER BY bidang').fetchall()]
    conn.close()
    return opts


def get_kabkota(provinsi=None):
    conn = get_conn()
    if provinsi:
        rows = conn.execute(
            'SELECT DISTINCT kab_kota FROM osn_siswa WHERE provinsi = ? ORDER BY kab_kota',
            (provinsi,)
        ).fetchall()
    else:
        rows = conn.execute('SELECT DISTINCT kab_kota FROM osn_siswa ORDER BY kab_kota').fetchall()
    conn.close()
    return [r[0] for r in rows]


# ── Query builder ────────────────────────────────────────────────

def build_where(filters):
    """Bangun klausa WHERE dan params dari dict filter.
    Mendukung multi-value (list) untuk kategori, provinsi, kab_kota.
    """
    clauses, params = [], []

    # Single-select
    for col in ['tahun', 'bidang']:
        val = filters.get(col)
        if val and val != 'semua':
            clauses.append(f'{col} = ?')
            params.append(val)

    # Multi-select
    for col in ['kategori', 'provinsi', 'kab_kota']:
        val = filters.get(col)
        if not val:
            continue
        # Bisa berupa list atau string tunggal
        if isinstance(val, str):
            val = [v for v in val.split(',') if v and v != 'semua']
        else:
            val = [v for v in val if v and v != 'semua']
        if val:
            placeholders = ','.join('?' * len(val))
            clauses.append(f'{col} IN ({placeholders})')
            params.extend(val)

    where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
    return where, params



# ── Pivot queries ────────────────────────────────────────────────

PIVOT_SELECT = """
    SUM(lolos_osnp)       AS lolos_osnp,
    SUM(lolos_osnsf)      AS lolos_osnsf,
    SUM(lolos_osnf)       AS lolos_osnf,
    SUM(jadi_medalis)     AS jadi_medalis
"""

SORT_BY = "ORDER BY jadi_medalis DESC, lolos_osnf DESC, lolos_osnsf DESC, lolos_osnp DESC"


def pivot_provinsi(filters):
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT provinsi, kategori, {PIVOT_SELECT}
        FROM osn_siswa {where}
        GROUP BY provinsi, kategori
        {SORT_BY}
    """, conn, params=params)
    conn.close()
    return df


def pivot_kabkota(filters):
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT provinsi, kategori, kab_kota, {PIVOT_SELECT}
        FROM osn_siswa {where}
        GROUP BY provinsi, kategori, kab_kota
        {SORT_BY}
    """, conn, params=params)
    conn.close()
    return df


def pivot_sekolah(filters):
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT provinsi, kategori, kab_kota, sekolah, {PIVOT_SELECT}
        FROM osn_siswa {where}
        GROUP BY provinsi, kategori, kab_kota, sekolah
        {SORT_BY}
    """, conn, params=params)
    conn.close()
    return df

def summary_cards(filters):
    """Angka ringkasan untuk kartu di atas dashboard."""
    where, params = build_where(filters)
    conn = get_conn()
    row = conn.execute(f"""
        SELECT
            SUM(lolos_osnp)   AS total_lolos_osnp,
            SUM(lolos_osnsf)  AS total_lolos_osnsf,
            SUM(lolos_osnf)   AS total_lolos_osnf,
            SUM(jadi_medalis) AS total_medalis
        FROM osn_siswa {where}
    """, params).fetchone()
    conn.close()
    return dict(row)


def chart_by_bidang(filters):
    """Data untuk grafik batang per bidang."""
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT bidang,
               SUM(lolos_osnp)   AS lolos_osnp,
               SUM(lolos_osnsf)  AS lolos_osnsf,
               SUM(lolos_osnf)   AS lolos_osnf,
               SUM(jadi_medalis) AS jadi_medalis
        FROM osn_siswa {where}
        GROUP BY bidang
        ORDER BY lolos_osnp DESC
    """, conn, params=params)
    conn.close()
    return df


def funnel_data(filters):
    """Data funnel tahapan OSN — filter bidang diabaikan."""
    # Buat filters tanpa bidang
    f = {k: v for k, v in filters.items() if k != 'bidang'}
    where, params = build_where(f)
    conn = get_conn()
    row = conn.execute(f"""
        SELECT
            SUM(lolos_osnp)   AS lolos_osnp,
            SUM(lolos_osnsf)  AS lolos_osnsf,
            SUM(lolos_osnf)   AS lolos_osnf,
            SUM(jadi_medalis) AS jadi_medalis
        FROM osn_siswa {where}
    """, params).fetchone()
    conn.close()
    return dict(row)


def map_data(filters):
    """Data per provinsi untuk peta — filter bidang & kab_kota diabaikan."""
    f = {k: v for k, v in filters.items() if k not in ['bidang', 'kab_kota']}
    where, params = build_where(f)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT
            provinsi,
            SUM(lolos_osnp)   AS lolos_osnp,
            SUM(lolos_osnsf)  AS lolos_osnsf,
            SUM(lolos_osnf)   AS lolos_osnf,
            SUM(jadi_medalis) AS jadi_medalis
        FROM osn_siswa {where}
        GROUP BY provinsi
        ORDER BY lolos_osnp DESC
    """, conn, params=params)
    conn.close()
    return df