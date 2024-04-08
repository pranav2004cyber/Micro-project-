import streamlit as st
import sounddevice as sd
import soundfile as sf
import requests
import tempfile
import os
import time
import base64
import hashlib
import hmac


def record_audio(duration, filename):
    fs = 44100
    seconds = duration
    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype='int16')
    sd.wait()
    sf.write(filename, myrecording, fs)

def recognize_music(audio_file):
    access_key = "df24e314ee28b264102bc956f9de9c2e"
    access_secret = "zN2ZLHTCOPXQQePSH7uXqasvcOtsjxVVTY8FZS6F"
    requrl = "https://identify-ap-southeast-1.acrcloud.com/v1/identify"

    http_method = "POST"
    http_uri = "/v1/identify"
    data_type = "audio"
    signature_version = "1"
    timestamp = time.time()

    string_to_sign = http_method + "\n" + http_uri + "\n" + access_key + "\n" + data_type + "\n" + signature_version + "\n" + str(
        timestamp)

    sign = base64.b64encode(hmac.new(access_secret.encode('ascii'), string_to_sign.encode('ascii'),
                                    digestmod=hashlib.sha1).digest()).decode('ascii')


    files = [
        ('sample', ('test.wav', audio_file, 'audio/mpeg'))
    ]
    data = {'access_key': access_key,
            'sample_bytes': 1000,
            'timestamp': str(timestamp),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version}

    r = requests.post(requrl, files=files, data=data)
    r.encoding = "utf-8"
    if r.status_code == 200:
        data = r.json()
        return data
    else:
        return None


def main():
    st.set_page_config(
    page_title=" Harmony Hunter || music Recognizing system",
    page_icon="🎧"
)
    st.title("🎧 Harmony Hunter")
    st.write("Welcome to Harmony Hunter! This tool recognizes music played on your surroundings and identifies them. Just select duration below and hit the 'Record audio' button.")

    duration = st.slider("Select duration of recording (in seconds):", min_value=1, max_value=30, value=10)

    if st.button("Record Audio✨"):
        with st.spinner("Recording..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                record_audio(duration, tmp_audio.name)
                st.success("Recording saved.")
                st.audio(tmp_audio.name, format='audio/wav')
                st.write("Recognizing music...🪄")
                time.sleep(1)
                with open(tmp_audio.name, "rb") as f:
                    recognition = recognize_music(f)
                if recognition:
                    st.write("Title:", recognition.get("metadata", {}).get("music", [{}])[0].get("title"))
                    st.write("Artists:", recognition.get("metadata", {}).get("music", [{}])[0].get("artists")[0].get("name", {}))
                    st.write("Album:", recognition.get("metadata", {}).get("music", [{}])[0].get("album", {}).get("name"))
                else:
                    st.error("Unable to recognize music.")
            time.sleep(1)
            os.remove(tmp_audio.name)

if __name__ == "__main__":
    main()
