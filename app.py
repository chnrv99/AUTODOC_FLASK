import datetime
from docxtpl import DocxTemplate
from pathlib import Path
from flask import Flask, render_template
from flask import request
# import request
import docx

import os
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/uploads/')

def populate2(filename,context):
    # filename='vendor-contract'
    document_path = Path(__file__).parent / ('static/uploads/' + filename + '.docx')
    doc = DocxTemplate(document_path)

    context = context
    # return context
    # num = 2

    doc.render(context)
    doc.save(Path(__file__).parent / f"{filename[0:2]}-contract.docx")
    # print("Hello")


# to upload a file and filename
@app.route('/')
def home():
    return render_template('forms.html')

# filenames = []
# filename = ''
# a post request to handle the file upload
@app.route('/uploader', methods=['GET','POST'])
def uploader():
    if request.method == 'POST':
        f = request.files['file1']
        filename = request.form.get("filename")
        f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
        print(filenames)
        if filename in filenames:
            return 'already exists'
        else:
            filenames.append(filename)
            return filename

#to get the  inputs from user for the extracted variables
@app.route('/input')
def input():
    print(filenames)
    return render_template('input.html',filenames=filenames)

@app.route('/inputypes', methods = ['GET','POST'])
def inputypes():
    filename = request.form.get('filename')
    print(filename)

    doc = docx.Document('static/uploads/' + filename + '.docx')
 
# read in each paragraph in file
# result = [p.text for p in doc.paragraphs]
# print(result)

# for p in doc.paragraphs:
    #     print(p.text)

    l=[]

    for p in doc.paragraphs:
        a=p.text
        s=''
        for i in range(len(a)):
            if a[i]=='{' and a[i+1]=='{':
                i+=2
                while(a[i]!='}'):
                    s=s+a[i]
                    i+=1
            if s!='' and s not in l:
                l.append(s)
            s=''
    # populate(filename)
    return render_template('inputypes.html',l=l)


# populating and downloading the file
@app.route('/populate', methods=['GET','POST'])
def populate():
    filename = request.form.get('filename')
    # l = request.form[1:]
    # filename='vendor-contract'
    # document_path = Path(__file__).parent / ('static/uploads/' + filename + '.docx')
    # doc = DocxTemplate(document_path)

    # client = "Sven"
    # vendor = "Tutorial Ltd."
    # amount = 2105
    # non_refundable = round(amount * 0.2, 2)
    # line1 = "Some text goes here"
    # line2 = "...and here goes some more text"
    # today = datetime.datetime.today()
    # today_in_one_week = today + datetime.timedelta(days=7)

    # context = {
    #     "CLIENT": client,
    #     "VENDOR": vendor,
    #     "LINE1": line1,
    #     "LINE2": line2,
    #     "AMOUNT": amount,
    #     "NONREFUNDABLE": non_refundable,
    #     "TODAY": today.strftime("%Y-%m-%d"),
    #     "TODAY_IN_ONE_WEEK": today_in_one_week.strftime("%Y-%m-%d"),
    # }
    
    context={}
    cont = request.form
    for i,j in cont.items():
        context[i]=j
    filename = request.form.get('filename')
    populate2(filename,context)
    return str(len(cont))
    # doc.render(context)
    # doc.save(Path(__file__).parent / f"{vendor}-contract.docx")

    # return render_template('populate.html')
