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
        ydl_opts = {'quiet': True, 'no_warnings': True, 'format': 'best'}
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Извлекаем страну/регион
            country = info.get('location') or info.get('region') or info.get('country')
            if not country and 'webpage_url_domain' in info:
                # Если TikTok не дал страну, попробуем угадать по домену или оставить N/A
                country = "Global/TikTok"

            fps = info.get('fps')
            if not fps and 'formats' in info:
                fps = next((f.get('fps') for f in info['formats'] if f.get('fps')), 60)

            filesize = info.get('filesize') or info.get('filesize_approx')
            if not filesize and 'formats' in info:
                filesize = next((f.get('filesize') or f.get('filesize_approx') for f in info['formats'] if f.get('filesize')), 0)
            
            return jsonify({
                "status": "success",
                "quality": f"{info.get('width', '?')}x{info.get('height', '?')}",
                "fps": int(fps) if fps else 60,
                "size": f"{round(filesize / 1048576, 2)} MB" if filesize else "Unknown",
                "country": country if country else "International"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
