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
        # Настройки для глубокого поиска метаданных
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best', 
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # 1. Глубокий поиск FPS
            fps = info.get('fps')
            if not fps and info.get('formats'):
                # Если в корне нет, перебираем все форматы
                for f in info['formats']:
                    if f.get('fps'):
                        fps = f.get('fps')
                        break

            # 2. Глубокий поиск размера файла
            filesize = info.get('filesize') or info.get('filesize_approx')
            if not filesize and info.get('formats'):
                for f in info['formats']:
                    size = f.get('filesize') or f.get('filesize_approx')
                    if size:
                        filesize = size
                        break
            
            # Форматируем вывод
            size_str = f"{round(filesize / (1024 * 1024), 2)} MB" if filesize else "Unknown"
            fps_str = f"{int(fps)}" if fps else "N/A"

            return jsonify({
                "status": "success",
                "quality": f"{info.get('width', '?')}x{info.get('height', '?')}",
                "fps": fps_str,
                "size": size_str
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Порт для Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
