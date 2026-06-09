import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'osn_lopi_dashboard.db'


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
    """Bangun klausa WHERE dan params dari dict filter."""
    clauses, params = [], []
    for col in ['tahun', 'kategori', 'provinsi', 'kab_kota', 'bidang']:
        val = filters.get(col)
        if val and val != 'semua':
            clauses.append(f'{col} = ?')
            params.append(val)
    where = ('WHERE ' + ' AND '.join(clauses)) if clauses else ''
    return where, params


# ── Pivot queries ────────────────────────────────────────────────

PIVOT_SELECT = """
    SUM(lolos_osnp)       AS lolos_osnp,
    SUM(lolos_osnsf)      AS lolos_osnsf,
    SUM(lolos_osnf)       AS lolos_osnf,
    SUM(jadi_medalis)     AS jadi_medalis
"""


def pivot_provinsi(filters):
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT provinsi, {PIVOT_SELECT}
        FROM osn_siswa {where}
        GROUP BY provinsi
        ORDER BY lolos_osnp DESC
    """, conn, params=params)
    conn.close()
    return df


def pivot_kabkota(filters):
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT provinsi, kab_kota, {PIVOT_SELECT}
        FROM osn_siswa {where}
        GROUP BY provinsi, kab_kota
        ORDER BY provinsi, lolos_osnp DESC
    """, conn, params=params)
    conn.close()
    return df


def pivot_sekolah(filters):
    where, params = build_where(filters)
    conn = get_conn()
    df = pd.read_sql_query(f"""
        SELECT provinsi, kab_kota, sekolah, npsn, {PIVOT_SELECT}
        FROM osn_siswa {where}
        GROUP BY provinsi, kab_kota, sekolah
        ORDER BY provinsi, kab_kota, lolos_osnp DESC
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