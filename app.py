import json

import requests
from flask import Flask, render_template, request, flash
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from flask_wtf.file import FileAllowed
from werkzeug.utils import secure_filename
import os, sys
from pypdf import PdfReader
from wtforms.fields.simple import StringField

from resumeparser import ats_extractor

# from resumeparser import ats_extractor

app = Flask(__name__)

# API KEYS
RESUME_PARSER_API_KEY = "UNQfgDLJNrFMJAEdku5GjqxFbGj7sfSM"

app.config['SECRET_KEY'] = 'akhilantarura'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("Upload the resume in PDF* or *DOCX", validators=[FileAllowed(['pdf', 'docx'], 'Only PDF and Word Files are allowed!')])
    submit = SubmitField("Submit")
    job_role = StringField("Job Role")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resume_analyze', methods=["GET", "POST"])
def resume_page():
    form = UploadFileForm()

    if request.method == "GET":
        return render_template('example.html', form=form);

    if form.validate_on_submit():
        job_role = form.job_role.data
        file = form.file.data
        print('File Received')

        if file and allowed_file(file.filename):
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            flash("File has been uploaded successfully!", "success")

            # CODE FOR THE FILE START----------
            file_name = file.filename
            file_path = f"static/files/{file_name}"
            print(f"FILE PATH : {file_path}")
            print(f"FILE NAME : {file_name}")

            # RISK START

            data = _read_file_from_path(file_path)
            data = ats_extractor(data, job_role)

            for text in data:
                text.replace("*", "")
                text=text.lstrip()
                print(text)
                print('\n\n\n')
            # RISK END

            # CODE FOR THE FILE END----------

            return render_template('example.html', form=form, parsed_text = data[0], ats_text = data[1], keywords_text=data[2], errors_text=data[3], suggestions_text=data[4], news_text=data[5], jpeg_file=data[6])
        else:
            flash("Invalid File Type, supports only PDF and WordX")

    return render_template('example.html', form=form)

def _read_file_from_path(path):
    reader = PdfReader(path)
    data = ""

    for page_no in range(len(reader.pages)):
        page = reader.pages[page_no]
        data += page.extract_text()

    return data

def allowed_file(filename):
    allowed_extension = {'pdf', 'docx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extension

if __name__ == '__main__':
    app.run(debug=True)
