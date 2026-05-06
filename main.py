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
        # Настройки для более глубокого анализа метаданных
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best', 
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Ищем FPS в разных полях, так как TikTok может его прятать
            fps = info.get('fps')
            if not fps and info.get('formats'):
                # Проверяем все доступные форматы видео
                for f in info['formats']:
                    if f.get('fps'):
                        fps = f.get('fps')
                        break

            # Ищем размер файла (точный или примерный)
            filesize = info.get('filesize') or info.get('filesize_approx')
            if not filesize and info.get('formats'):
                for f in info['formats']:
                    if f.get('filesize') or f.get('filesize_approx'):
                        filesize = f.get('filesize') or f.get('filesize_approx')
                        break
            
            size_str = f"{round(filesize / (1024 * 1024), 2)} MB" if filesize else "Unknown"

            return jsonify({
                "status": "success",
                "quality": f"{info.get('width', '?')}x{info.get('height', '?')}",
                "fps": fps if fps else "N/A",
                "size": size_str
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Настройки порта для Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
