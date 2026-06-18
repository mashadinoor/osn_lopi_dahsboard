"""
Migrasi data dari SQLite lokal ke Supabase PostgreSQL.

Sebelum jalankan:
    pip install psycopg2-binary

Cara pakai:
    python migrate_to_supabase.py
"""
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# ── KONFIGURASI — sesuaikan dulu ──────────────────────────────────
SQLITE_PATH = 'data/osn_dashboard.db'

# Connection string Supabase — ambil dari:
# Supabase Dashboard > Project Settings > Database > Connection string > URI
# Format: postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
SUPABASE_URL = 'postgresql://postgres.tlxtnssmxomyiwfmjwwv:085722-Maulana@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres'
# ────────────────────────────────────────────────────────────────


def main():
    # 1. Baca semua data dari SQLite
    print('Membaca data dari SQLite...')
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    rows = sqlite_conn.execute('SELECT * FROM osn_siswa').fetchall()
    sqlite_conn.close()
    print(f'  Total: {len(rows)} baris')

    if not rows:
        print('Tidak ada data untuk dimigrasi.')
        return

    # 2. Siapkan kolom (tanpa id, biar auto-increment di Postgres)
    columns = [k for k in rows[0].keys() if k != 'id']
    print(f'  Kolom: {columns}')

    # 3. Convert ke list of tuples
    data = [tuple(row[col] for col in columns) for row in rows]

    # 4. Connect ke Supabase dan insert
    print('\nMenghubungkan ke Supabase...')
    pg_conn = psycopg2.connect(SUPABASE_URL)
    pg_cur = pg_conn.cursor()

    # Kosongkan tabel dulu (kalau re-run script ini)
    pg_cur.execute('TRUNCATE TABLE osn_siswa RESTART IDENTITY')

    # Insert pakai execute_values (lebih cepat untuk bulk insert)
    insert_query = f"""
        INSERT INTO osn_siswa ({', '.join(columns)})
        VALUES %s
    """
    print('Mengupload data ke Supabase...')
    execute_values(pg_cur, insert_query, data, page_size=500)

    pg_conn.commit()

    # 5. Validasi
    pg_cur.execute('SELECT COUNT(*) FROM osn_siswa')
    total = pg_cur.fetchone()[0]
    print(f'\n✓ Done! Total baris di Supabase: {total}')

    pg_cur.close()
    pg_conn.close()


if __name__ == '__main__':
    main()