from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os

app = Flask(__name__)

# Gunakan folder lokal yang pasti punya izin tulis
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')
    
    # Gunakan format 'worst' atau 'bestvideo+bestaudio/best' untuk tes
    # Di sini kita pakai 'best' agar tidak terlalu berat saat merging
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Ambil info tanpa download dulu untuk cek koneksi
            # Jika bagian ini lolos, berarti VPN bekerja
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return "Gagal mendapatkan info. Cek link atau VPN."

            # 2. Lakukan download secara nyata
            ydl.download([url])
            
            filename = ydl.prepare_filename(info)
            base_name = os.path.basename(filename)
            
            return f"""
            <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
                <h2 style="color: green;">✅ Berhasil!</h2>
                <p>{base_name}</p>
                <a href='/get-file/{base_name}' style='padding:10px; background:blue; color:white; text-decoration:none; border-radius:5px;'>Download ke Galeri</a>
                <br><br><a href='/'>Kembali</a>
            </div>
            """
            
    except Exception as e:
        # Menangani error koneksi spesifik
        err_msg = str(e)
        if "104" in err_msg or "reset" in err_msg:
            return "Koneksi diputus. Coba ganti server VPN ke negara lain (misal: Singapura/USA)."
        return f"Error: {err_msg}"

@app.route('/get-file/<filename>')
def get_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    # Render akan menentukan port secara otomatis lewat environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
