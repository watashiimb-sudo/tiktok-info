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
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "status": "success",
                "quality": f"{info.get('width')}x{info.get('height')}",
                "fps": info.get('fps', 'N/A'),
                "size": f"{round(info.get('filesize_approx', 0) / 1024 / 1024, 2)} MB" if info.get('filesize_approx') else "Unknown"
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Важно: порт берется из переменной окружения для Railway/Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
