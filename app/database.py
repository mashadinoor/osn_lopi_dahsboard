import psycopg2
import psycopg2.extras
import pandas as pd
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")


def get_conn():
    conn = psycopg2.connect(SUPABASE_URL)
    return conn


def get_dict_cursor(conn):
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


# ── Filter options ──────────────────────────────────────────────

def get_filter_options():
    conn = get_conn()
    cur = conn.cursor()
    opts = {}
    cur.execute('SELECT DISTINCT tahun FROM osn_siswa ORDER BY tahun')
    opts['tahun'] = [r[0] for r in cur.fetchall()]
    cur.execute('SELECT DISTINCT kategori FROM osn_siswa ORDER BY kategori')
    opts['kategori'] = [r[0] for r in cur.fetchall()]
    cur.execute('SELECT DISTINCT provinsi FROM osn_siswa ORDER BY provinsi')
    opts['provinsi'] = [r[0] for r in cur.fetchall()]
    cur.execute('SELECT DISTINCT bidang FROM osn_siswa ORDER BY bidang')
    opts['bidang'] = [r[0] for r in cur.fetchall()]
    cur.close()
    conn.close()
    return opts


def get_kabkota(provinsi=None):
    conn = get_conn()
    cur = conn.cursor()
    if provinsi:
        cur.execute(
            'SELECT DISTINCT kab_kota FROM osn_siswa WHERE provinsi = %s ORDER BY kab_kota',
            (provinsi,)
        )
    else:
        cur.execute('SELECT DISTINCT kab_kota FROM osn_siswa ORDER BY kab_kota')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [r[0] for r in rows]


# ── Query builder ────────────────────────────────────────────────

def build_where(filters):
    clauses, params = [], []

    for col in ['tahun', 'bidang']:
        val = filters.get(col)
        if val and val != 'semua':
            clauses.append(f'{col} = %s')
            params.append(val)

    for col in ['kategori', 'provinsi', 'kab_kota']:
        val = filters.get(col)
        if not val:
            continue
        if isinstance(val, str):
            val = [v for v in val.split(',') if v and v != 'semua']
        else:
            val = [v for v in val if v and v != 'semua']
        if val:
            placeholders = ','.join(['%s'] * len(val))
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
    where, params = build_where(filters)
    conn = get_conn()
    cur = get_dict_cursor(conn)
    cur.execute(f"""
        SELECT
            SUM(lolos_osnp)   AS total_lolos_osnp,
            SUM(lolos_osnsf)  AS total_lolos_osnsf,
            SUM(lolos_osnf)   AS total_lolos_osnf,
            SUM(jadi_medalis) AS total_medalis
        FROM osn_siswa {where}
    """, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row)


def chart_by_bidang(filters):
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
    f = {k: v for k, v in filters.items() if k != 'bidang'}
    where, params = build_where(f)
    conn = get_conn()
    cur = get_dict_cursor(conn)
    cur.execute(f"""
        SELECT
            SUM(lolos_osnp)   AS lolos_osnp,
            SUM(lolos_osnsf)  AS lolos_osnsf,
            SUM(lolos_osnf)   AS lolos_osnf,
            SUM(jadi_medalis) AS jadi_medalis
        FROM osn_siswa {where}
    """, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return dict(row)


def map_data(filters):
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

def pivot_by_bidang(filters, pivot_type, tahapan_col):
    """
    Pivot Mode B: Bidang sebagai kolom, wilayah sebagai baris.
    Value sel = jumlah siswa pada tahapan OSN tertentu (tahapan_col).
    tahapan_col: salah satu dari 'lolos_osnp', 'lolos_osnsf', 'lolos_osnf', 'jadi_medalis'
    pivot_type: 'provinsi', 'kabkota', atau 'sekolah'
    Semua wilayah ditampilkan (tidak dibatasi top 5).
    """
    valid_cols = {'lolos_osnp', 'lolos_osnsf', 'lolos_osnf', 'jadi_medalis'}
    if tahapan_col not in valid_cols:
        raise ValueError(f'tahapan_col tidak valid: {tahapan_col}')

    where, params = build_where(filters)
    conn = get_conn()

    if pivot_type == 'provinsi':
        group_cols = ['provinsi']
    elif pivot_type == 'kabkota':
        group_cols = ['provinsi', 'kab_kota']
    elif pivot_type == 'sekolah':
        group_cols = ['provinsi', 'kab_kota', 'sekolah']
    else:
        raise ValueError(f'pivot_type tidak valid: {pivot_type}')

    select_cols = ', '.join(group_cols)

    df = pd.read_sql_query(f"""
        SELECT {select_cols}, bidang,
               SUM({tahapan_col}) AS nilai
        FROM osn_siswa {where}
        GROUP BY {select_cols}, bidang
    """, conn, params=params)

    conn.close()

    if df.empty:
        return {'group_cols': group_cols, 'bidang_list': [], 'rows': []}

    # Pivot: baris = wilayah (group_cols), kolom = bidang
    pivot = df.pivot_table(
        index=group_cols, columns='bidang', values='nilai',
        aggfunc='sum', fill_value=0
    )

    bidang_list = sorted(pivot.columns.tolist())
    pivot = pivot[bidang_list]

    # Tambah kolom total
    pivot['Total'] = pivot.sum(axis=1)

    # Urutkan berdasarkan Total descending
    pivot = pivot.sort_values('Total', ascending=False)

    rows = []
    for idx, row in pivot.iterrows():
        if len(group_cols) == 1:
            idx = (idx,)
        row_dict = dict(zip(group_cols, idx))
        for b in bidang_list:
            row_dict[b] = int(row[b])
        row_dict['Total'] = int(row['Total'])
        rows.append(row_dict)

    return {
        'group_cols': group_cols,
        'bidang_list': bidang_list,
        'rows': rows,
    }