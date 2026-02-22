from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Folder tempat video disimpan sementara
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    
    # Settingan yt-dlp untuk kualitas terbaik (HD)
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return f"Terjadi kesalahan: {str(e)}"

if __name__ == '__main__':
    # Gunakan port dari sistem (penting untuk hosting seperti Render/Railway)
    # Jika tidak ada, default ke 5000
    port = int(os.environ.get("PORT", 5000))
    
    # debug=False untuk keamanan saat online
    app.run(host='0.0.0.0', port=port, debug=False)
