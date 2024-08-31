import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify
import yt_dlp
import subprocess
import os


app = Flask(__name__)

# FFmpeg'in yolu
FFMPEG_PATH = 'C:/Users/MelihG/Downloads/ffmpeg-master-latest-win64-gpl/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe'

# Ana sayfa route'u
@app.route('/')
def index():
    return render_template('index.html')  # index.html dosyasını göster

# Video bilgilerini getir
@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    url = request.json.get('url')
    
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',  # Video ve ses formatlarını birlikte seç
            'merge_output_format': 'mp4',  # FFmpeg ile birleştirme
            'noplaylist': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get('formats', [])
            thumbnail = info_dict.get('thumbnail', '')
            
            valid_heights = {144, 360, 480, 720, 1080, 1440, 2160, 4320}
            unique_streams = {}
            for fmt in formats:
                height = fmt.get('height')
                vcodec = fmt.get('vcodec')
                acodec = fmt.get('acodec')
                format_id = fmt.get('format_id')
                ext = fmt.get('ext', 'unknown')
                format_note = fmt.get('format_note', 'N/A')
                
                if vcodec and acodec:
                    if height in valid_heights:
                        resolution = f"{height}p"
                        if resolution not in unique_streams:
                            unique_streams[resolution] = (format_id, ext)

        available_streams = [(fmt_id, note, ext) for note, (fmt_id, ext) in unique_streams.items()]
        return jsonify({
            'success': True,
            'streams': available_streams,
            'thumbnail': thumbnail
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Video indirme işlemi
@app.route('/download_video', methods=['POST'])
def download_video_quality():
    video_url = request.form['video_url']
    format_id = request.form['format_id']

    try:
        ydl_opts = {
            'format': f'{format_id}+bestaudio[ext=m4a]',
            'outtmpl': 'downloads/%(title)s.mp4',
            'noplaylist': True,
            'quiet': True,
            'ffmpeg_location': FFMPEG_PATH,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        return jsonify({'message': 'Video başarıyla mp4 formatında indirildi!'})

    except Exception as e:
        return jsonify({'message': f"Bir hata oluştu: {str(e)}"})

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    Timer(1, open_browser).start()  # Sunucu başladıktan 1 saniye sonra tarayıcıyı açar
    app.run()

if __name__ == '__main__':
    app.run(debug=True)
