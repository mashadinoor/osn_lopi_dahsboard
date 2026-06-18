import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Membaca port secara dinamis dari Render, jika tidak ada (lokal) pakai 5000
    port = int(os.environ.get("PORT", 5000))
    
    # Matikan debug=True di production server untuk menghindari celah keamanan
    app.run(debug=False, host='0.0.0.0', port=port)