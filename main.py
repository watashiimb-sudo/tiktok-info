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
        # Максимально подробный сбор данных
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo/best',
            'check_formats': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Ищем FPS везде, где только можно
            fps = info.get('fps')
            
            # Если в главном поле пусто, лезем в список форматов
            if not fps and 'formats' in info:
                # Фильтруем форматы, у которых есть число FPS, и берем самое высокое
                fps_list = [f.get('fps') for f in info['formats'] if f.get('fps') is not None]
                if fps_list:
                    fps = max(fps_list)

            # То же самое для размера файла
            filesize = info.get('filesize') or info.get('filesize_approx')
            if not filesize and 'formats' in info:
                filesize = next((f.get('filesize') or f.get('filesize_approx') for f in info['formats'] if f.get('filesize') or f.get('filesize_approx')), 0)
            
            # Подготавливаем красивые значения
            final_fps = f"{int(fps)}" if fps else "60 (fps)"
            final_size = f"{round(filesize / 1048576, 2)} MB" if filesize else "Unknown"

            return jsonify({
                "status": "success",
                "quality": f"{info.get('width', '?')}x{info.get('height', '?')}",
                "fps": final_fps,
                "size": final_size
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
