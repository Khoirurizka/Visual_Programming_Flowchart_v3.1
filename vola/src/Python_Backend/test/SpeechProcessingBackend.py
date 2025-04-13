from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
SAVE_PATH = 'voice'
FILENAME = 'recording.wav'

os.makedirs(SAVE_PATH, exist_ok=True)

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file in request'}), 400

    file = request.files['audio']
    save_path = os.path.join(SAVE_PATH, FILENAME)
    file.save(save_path)

    print(f"Audio saved to {save_path}")
    return jsonify({'message': 'Audio saved', 'path': save_path}), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1',port=9000)
