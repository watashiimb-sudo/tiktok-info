import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/get_info', methods=['GET'])
def get_tiktok_info():
    video_url = request.args.get('link')
    if not video_url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    try:
        # Улучшенные настройки для извлечения скрытых данных
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo+bestaudio/best',
            'force_generic_extractor': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Извлекаем данные
            info = ydl.extract_info(video_url, download=False)
            
            # 1. Проверяем FPS в основном блоке или в форматах
            fps = info.get('fps')
            if not fps and 'formats' in info:
                # Берем FPS из первого попавшегося формата, где он указан
                fps = next((f.get('fps') for f in info['formats'] if f.get('fps')), None)

            # 2. Проверяем размер файла (filesize или filesize_approx)
            size_bytes = info.get('filesize') or info.get('filesize_approx')
            if not size_bytes and 'formats' in info:
                size_bytes = next((f.get('filesize') or f.get('filesize_approx') for f in info['formats'] if f.get('filesize') or f.get('filesize_approx')), 0)
            
            # Форматируем данные для отправки на сайт
            return jsonify({
                "status": "success",
                "quality": f"{info.get('width', '?')}x{info.get('height', '?')}",
                "fps": f"{int(fps)}" if fps else "60 (est.)", # Если не нашли, скорее всего это стандартные 60
                "size": f"{round(size_bytes / 1048576, 2)} MB" if size_bytes else "Unknown"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
