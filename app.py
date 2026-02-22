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
    
    # Folder /tmp adalah satu-satunya tempat yang diizinkan Vercel (sementara)
    download_path = '/tmp/%(title)s.%(ext)s'
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': download_path,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Mengambil info
            info = ydl.extract_info(url, download=True)
            if info is None:
                return "Gagal mengambil video. Link tidak valid atau tidak didukung."
                
            filename = ydl.prepare_filename(info)
            
            # Mengirim file langsung ke user lalu menghapusnya dari serverless
            return_data = io.BytesIO()
            with open(filename, 'rb') as fo:
                return_data.write(fo.read())
            return_data.seek(0)
            
            # Hapus file di server agar tidak memenuhi ram
            os.remove(filename)

            return send_file(
                return_data,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=os.path.basename(filename)
            )
            
    except Exception as e:
        return f"Error di Vercel: {str(e)}"

# PENTING: Untuk Vercel, jangan pakai if __name__ == '__main__'
