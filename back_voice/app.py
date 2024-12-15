from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import speech_recognition as sr
from pyngrok import ngrok
from difflib import SequenceMatcher
from pydub import AudioSegment
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)
CORS(app)  # Cho phép kết nối từ frontend

# Khởi tạo ngrok
NGROK_TOKEN = os.getenv('NGROK_TOKEN')  # Đọc token từ biến môi trường
if not NGROK_TOKEN:
    raise ValueError("Vui lòng cung cấp NGROK_TOKEN trong file .env!")
ngrok.set_auth_token(NGROK_TOKEN)
public_url = "http://127.0.0.1:4041"
print("Ngrok tunnel URL:", public_url)

# Hàm chuyển giọng nói thành văn bản
def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)

        print("Starting speech recognition...")
        text = recognizer.recognize_google(audio)
        print("Recognition successful:", text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Google Speech Recognition service error: {e}")
        return None
    except Exception as e:
        print(f"Error during speech recognition: {e}")
        return None

# Hàm so sánh văn bản
def compare_text(original, recognized):
    original_words = original.split()
    recognized_words = recognized.split()
    matcher = SequenceMatcher(None, original_words, recognized_words)
    differences = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            differences.append({"type": "replace", "original": original_words[i1:i2], "recognized": recognized_words[j1:j2]})
        elif tag == 'delete':
            differences.append({"type": "delete", "original": original_words[i1:i2], "recognized": []})
        elif tag == 'insert':
            differences.append({"type": "insert", "original": [], "recognized": recognized_words[j1:j2]})
    return differences

# Hàm chuyển đổi file âm thanh sang PCM WAV
def convert_to_pcm_wav(input_path, output_path):
    try:
        sound = AudioSegment.from_file(input_path)
        sound.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print("Lỗi chuyển đổi file:", e)
        return None

@app.route('/process_video', methods=['POST'])
def process_video():
    # Kiểm tra dữ liệu gửi lên
    if 'audio' not in request.files or 'reference_text' not in request.form:
        return jsonify({"error": "Thiếu file audio hoặc reference_text"}), 400

    audio_file = request.files['audio']
    reference_text = request.form['reference_text']

    # Lưu file âm thanh tạm thời
    audio_path = '/tmp/recorded_audio.wav'
    audio_file.save(audio_path)

    # Kiểm tra và chuyển đổi file nếu cần
    try:
        converted_audio_path = convert_to_pcm_wav(audio_path, '/tmp/converted_audio.wav')
        if not converted_audio_path:
            return jsonify({"error": "Không thể chuyển đổi file âm thanh"}), 500
    except Exception as e:
        print(f"Lỗi khi xử lý file âm thanh: {e}")
        return jsonify({"error": "Lỗi xử lý file âm thanh"}), 500

    # Nhận dạng giọng nói
    recognized_text = speech_to_text(converted_audio_path)
    if not recognized_text:
        return jsonify({"error": "Không thể nhận dạng giọng nói"}), 500

    # So sánh văn bản
    differences = compare_text(reference_text, recognized_text)

    return jsonify({
        "recognized_text": recognized_text,
        "differences": differences
    })
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
