from flask import Flask, render_template, request
import requests
import base64
import pyaudio
import wave

app = Flask(__name__)

def record_audio(file_path, duration=5, sample_rate=44100, chunk=1024):
    try:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=sample_rate, input=True, frames_per_buffer=chunk)
        frames = []
        for i in range(0, int(sample_rate / chunk * duration)):
            data = stream.read(chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        return True
    except Exception as e:
        print("Error recording audio:", str(e))
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    if record_audio('temp_audio.wav'):
        file_path = 'temp_audio.wav'
        with open(file_path, "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode("utf-8")
        
        shazam_api_url = "https://shazam.p.rapidapi.com/v1/songs/detect"
        
        api_key = "87a2c6ae75mshd14843588d76ca9p1fa32djsn766fca1e740e"
        headers = {
            "X-RapidAPI-Host": "shazam.p.rapidapi.com",
            "X-RapidAPI-Key": api_key,
            "Content-Type": "application/json",
        }
        
        data = {"audio": {"value": audio_base64}}
        
        response = requests.post(shazam_api_url, json=data, headers=headers)
        
        if response.status_code == 200:
            song_info = response.json()
            if "track" in song_info:
                track_title = song_info["track"]["title"]
                artist_name = song_info["track"]["subtitle"]
                return f"Song: {track_title} | Artist: {artist_name}"
            else:
                return "Song not recognized"
        else:
            return f"Error: {response.status_code}"
    else:
        return "Error recording audio"

if __name__ == '__main__':
    app.run(debug=True)
