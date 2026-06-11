import sqlite3
conn = sqlite3.connect('data/osn_dashboard.db')
rows = conn.execute("""
    SELECT DISTINCT kab_kota FROM osn_siswa 
    WHERE provinsi = 'JAWA TENGAH'
    ORDER BY kab_kota LIMIT 10
""").fetchall()
for r in rows: print(r[0])
