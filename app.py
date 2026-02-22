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
    
    # Lokasi penyimpanan sementara di Vercel
    download_path = '/tmp/%(title)s.%(ext)s'
    
    # Konfigurasi ydl_opts terbaru untuk menyamar sebagai browser asli
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': download_path,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        },
        'merge_output_format': 'mp4',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Mengambil info dan download
            info = ydl.extract_info(url, download=True)
            if info is None:
                return "Gagal mengambil video. Link tidak valid atau server diblokir."
            
            filename = ydl.prepare_filename(info)
            
            # Membaca file ke memori (BytesIO)
            return_data = io.BytesIO()
            with open(filename, 'rb') as f:
                return_data.write(f.read())
            return_data.seek(0)
            
            # Hapus file dari penyimpanan sementara /tmp
            if os.path.exists(filename):
                os.remove(filename)

            return send_file(
                return_data,
                as_attachment=True,
                download_name=os.path.basename(filename),
                mimetype='video/mp4'
            )
            
    except Exception as e:
        # Menampilkan pesan error detail untuk debugging
        return f"Terjadi kesalahan teknis: {str(e)} <br><a href='/'>Coba Lagi</a>"

# Variabel app diposisi global untuk deployment Vercel
app = app
