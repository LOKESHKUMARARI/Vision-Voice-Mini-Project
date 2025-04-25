from flask import Flask, render_template, request, jsonify, redirect, url_for
from gtts import gTTS
import google.generativeai as genai
import base64
import io
import os
import PIL.Image
from googletrans import Translator

app = Flask(__name__, static_folder='static')  # Ensure static folder is configured

# Configure Translator
translator = Translator()

# Set your Gemini API Key
 
genai.configure(api_key=os.environ.get("AIzaSyB4Go6j0e342y5l7mSvzyb4BWTDZFcW7oM"))


# Routes
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

        image_data = data['image'].split(',')[1]
        image_binary = base64.b64decode(image_data)

        with open('captured_image.png', 'wb') as f:
            f.write(image_binary)

        img = PIL.Image.open(io.BytesIO(image_binary))

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Describe the scene in the image using beautiful and simple language", img
        ])
        response.resolve()

        tts = gTTS(text=response.text, lang='en')
        output_path = os.path.join('static', 'output.mp3')
        tts.save(output_path)

        return redirect(url_for('result'))

    except Exception as e:
        print("Upload Error:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/upload2', methods=['POST'])
def upload2():
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            print("No image data found in request.")
            return jsonify({'error': 'No image data provided'}), 400

        image_data = data['image'].split(',')[1]
        image_binary = base64.b64decode(image_data)

        with open('captured_image.png', 'wb') as f:
            f.write(image_binary)

        img = PIL.Image.open(io.BytesIO(image_binary))

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([
            "Describe the scene in the image using beautiful and simple language", img
        ])
        response.resolve()

        translated_text = translator.translate(response.text, dest='ta').text
        print("Translated Text:", translated_text)

        tts = gTTS(text=translated_text, lang='ta')
        output_path = os.path.join('static', 'output.mp3')
        tts.save(output_path)

        return redirect(url_for('result'))

    except Exception as e:
        print("Upload2 Error:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/gpt', methods=['GET', 'POST'])
def gpt():
    response_text = ""
    encoded_string = ""

    if request.method == 'POST':
        transcribed_text = request.form.get('transcribed_text')

        if transcribed_text:
            model = genai.GenerativeModel('gemini-pro')
            rply = model.generate_content("explain in 3 lines " + transcribed_text)
            response_text = rply.text

            tts = gTTS(text=response_text, lang='en')
            output_path = os.path.join('static', 'output.mp3')
            tts.save(output_path)


            with open("static/response.mp3", "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
        else:
            response_text = "No input provided."

    return render_template('gpt.html', response=response_text, audio=encoded_string)

@app.route('/result')
def result():
    audio_url = url_for('static', filename='output.mp3')
    return render_template('result.html', audio=audio_url)

if __name__ == '__main__':
    app.run(debug=True)
