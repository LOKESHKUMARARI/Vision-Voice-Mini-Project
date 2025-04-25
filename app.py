from flask import Flask, render_template, request, jsonify, redirect, url_for
from gtts import gTTS
import google.generativeai as genai
import base64
import io
import os
import PIL.Image
from googletrans import Translator

app = Flask(__name__)
translator = Translator()

# Configure Generative AI
genai.configure(api_key="AIzaSyB4Go6j0e342y5l7mSvzyb4BWTDZFcW7oM")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/scan2')
def scan2():
    return render_template('scan2.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        image_data = data['image']
        image_data = image_data.split(',')[1]
        image_binary = base64.b64decode(image_data)

        with open('captured_image.png', 'wb') as f:
            f.write(image_binary)

        img = PIL.Image.open(io.BytesIO(image_binary))

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(["Describe the scene in the image using beautiful and simple language", img], stream=True)
        response.resolve()

        tts = gTTS(text=response.text, lang='en')
        tts.save('static/output.mp3')

        return redirect(url_for('result'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload2', methods=['POST'])
def upload2():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        image_data = data['image']
        image_data = image_data.split(',')[1]
        image_binary = base64.b64decode(image_data)

        with open('captured_image.png', 'wb') as f:
            f.write(image_binary)

        img = PIL.Image.open(io.BytesIO(image_binary))

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(["Describe the scene in the image using beautiful and simple language", img], stream=True)
        response.resolve()

        translated_text = translator.translate(response.text, dest='ta').text
        tts = gTTS(text=translated_text, lang='ta')
        tts.save('static/output.mp3')

        return redirect(url_for('result'))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/gpt', methods=['GET', 'POST'])
def gpt():
    response_text = ""
    audio = ""
    if request.method == 'POST':
        transcribed_text = request.form.get('transcribed_text')

        if transcribed_text:
            model = genai.GenerativeModel('gemini-pro')
            rply = model.generate_content("explain in 3 lines " + transcribed_text)
            response_text = rply.text

            tts = gTTS(text=response_text, lang='en')
            tts.save('response.mp3')

            with open("response.mp3", "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
        else:
            response_text = "No input provided."
            encoded_string = ""

        return render_template('gpt.html', response=response_text, audio=encoded_string)
    else:
        return render_template('gpt.html')

@app.route('/result')
def result():
    audio_url = "output.mp3"
    return render_template('result.html', audio=audio_url)

if __name__ == '__main__':
    app.run(debug=True)
