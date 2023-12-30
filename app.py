from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from PyPDF2 import PdfReader

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)

        converted_text = None

        # Perform PDF to text conversion
        if file.filename.lower().endswith('.pdf'):
            converted_text = pdf_to_text(filename)

        if converted_text:
            # Save the converted text to a file
            txt_filename = os.path.splitext(file.filename)[0] + '_converted.txt'
            txt_path = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(converted_text)

            return render_template('download.html', txt_filename=txt_filename)

    return render_template('download.html', conversion_failed=True)

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
