from flask import Flask, redirect, render_template, request, json, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lelezoco85@localhost/unbabel'
else:
    app.debug = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Translation_request(db.Model):
    __tablename__= 'translation_request'
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Float, unique=True)
    price = db.Column(db.Float)
    source_language = db.Column(db.String(200))
    status = db.Column(db.String(200))
    target_language = db.Column(db.String(200))
    text = db.Column(db.Text())
    text_format = db.Column(db.String(200))
    uid = db.Column(db.String(200), unique=True)

    def __init__(self, order_number, price, source_language, status, target_language, text, text_format, uid):
        self.order_number = order_number
        self.price = price
        self.source_language = source_language
        self.status = status
        self.target_language = target_language
        self.text = text
        self.text_format = text_format
        self.uid = uid

username = "fullstack-challenge"
api_key = "9db71b322d43a6ac0f681784ebdcc6409bb83359"
URL = "https://sandbox.unbabel.com/tapi/v2/translation/"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'ApiKey {username}:{api_key}'
}


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route('/translate', methods=["GET", "POST"])
def translate():
    
## variables taken from the form to use in the translation request
    text_to_translate = request.form["textToTranslate"]
    source_language = request.form["sourceLanguage"]
    target_language = request.form["targetLanguage"]

    payload = {
        'text': f"{text_to_translate}",
        'source_language': f"{source_language}",
        'target_language': f"{target_language}"
        }
    
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    
    json_data = response.json()
   
    order_number = json_data["order_number"]
    price = json_data["price"]
    source_language = json_data["source_language"]
    status = json_data["status"]
    target_language = json_data["target_language"]
    text = json_data["text"]
    text_format = json_data["text_format"]
    uid = json_data["uid"]

   
    if source_language == target_language:
        return render_template("index.html", message = "Source language and target language must be different.") 
    if text_to_translate == "":
        return render_template("index.html", message="Please provide the text for translation")
    if response.ok:
        data = Translation_request(order_number,price, source_language, status, target_language, text, text_format, uid)
        db.session.add(data)
        db.session.commit()

        return render_template("index.html", message="Translation successifuly sent")


if __name__ == '__main__':
    app.run()
