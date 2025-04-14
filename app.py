from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Route 1: মেমোরির ভিডিও ফাইল দিয়ে লাইভ
@app.route('/live_from_file', methods=['POST'])
def live_from_file():
    file = request.files['video']
    rtmp_url = request.form['rtmp_url']

    if file:
        filename = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
        file.save(filename)

        ffmpeg_cmd = [
            'ffmpeg',
            '-re',
            '-i', filename,
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-maxrate', '3000k',
            '-bufsize', '6000k',
            '-pix_fmt', 'yuv420p',
            '-g', '50',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-f', 'flv',
            rtmp_url
        ]
        subprocess.Popen(ffmpeg_cmd)

        return jsonify({"message": "Live started from file!"})
    return jsonify({"error": "No file provided"}), 400


# Route 2: লিংক থেকে ভিডিও ডাউনলোড করে লাইভ চালানো
@app.route('/live_from_link', methods=['POST'])
def live_from_link():
    data = request.json
    video_url = data.get('video_url')
    rtmp_url = data.get('rtmp_url')

    if not video_url or not rtmp_url:
        return jsonify({"error": "Missing video_url or rtmp_url"}), 400

    filename = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")

    download_cmd = ['yt-dlp', '-o', filename, video_url]
    subprocess.run(download_cmd)

    ffmpeg_cmd = [
        'ffmpeg',
        '-re',
        '-i', filename,
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-maxrate', '3000k',
        '-bufsize', '6000k',
        '-pix_fmt', 'yuv420p',
        '-g', '50',
        '-c:a', 'aac',
        '-b:a', '128k',
        '-ar', '44100',
        '-f', 'flv',
        rtmp_url
    ]
    subprocess.Popen(ffmpeg_cmd)

    return jsonify({"message": "Live started from link!"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
