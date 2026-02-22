from flask import Flask, render_template, request, send_file
import yt_dlp
import os
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    
    # Lokasi penyimpanan sementara yang diizinkan oleh Vercel
    download_path = '/tmp/%(title)s.%(ext)s'
    
    # Konfigurasi ydl_opts yang kamu berikan
    ydl_opts = {
        'format': 'best',
        'outtmpl': download_path,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False, 
        'quiet': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Ambil informasi dan download file ke /tmp/
            info = ydl.extract_info(url, download=True)
            if info is None:
                return "Gagal mengambil video. Link mungkin salah atau diproteksi."
            
            # 2. Dapatkan path file yang baru saja didownload
            filename = ydl.prepare_filename(info)
            
            # 3. Baca file ke dalam memori agar bisa langsung dikirim ke browser
            return_data = io.BytesIO()
            with open(filename, 'rb') as f:
                return_data.write(f.read())
            return_data.seek(0)
            
            # 4. Hapus file asli di folder /tmp/ agar tidak memenuhi penyimpanan server
            if os.path.exists(filename):
                os.remove(filename)

            # 5. Kirim file ke user sebagai attachment
            return send_file(
                return_data,
                as_attachment=True,
                download_name=os.path.basename(filename),
                mimetype='application/octet-stream'
            )
            
    except Exception as e:
        # Menampilkan error asli jika terjadi kegagalan (karena ignoreerrors: False)
        return f"Terjadi kesalahan teknis: {str(e)} <br><a href='/'>Coba Lagi</a>"

# Vercel tidak membutuhkan app.run() di dalam __main__
# Cukup pastikan variabel 'app' tersedia untuk dipanggil serverless function
