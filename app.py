from flask import Flask, redirect, render_template, request, json, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# development config
ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lelezoco85@localhost/unbabel'
else:
    app.debug = False 
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# creating database to retrieve response data

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

# variables for the request header
username = "fullstack-challenge"
api_key = "9db71b322d43a6ac0f681784ebdcc6409bb83359"
URL = "https://sandbox.unbabel.com/tapi/v2/translation/"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'ApiKey {username}:{api_key}'
}

# app routes
@app.route('/', methods=["GET", "POST"])
def index():
    list = Translation_request.query.all()
    print(list)
    return render_template("index.html", list=list)


@app.route('/translate', methods=["GET", "POST"])
def translate():
    
# values are retrieved from form inputs
    form_to_translate = request.form["textToTranslate"]
    form_source_lang = request.form["sourceLanguage"]
    form_target_lang = request.form["targetLanguage"]

# preparing the json and sending it to translation request endpoint
    payload = {
        'text': f"{form_to_translate}",
        'source_language': f"{form_source_lang}",
        'target_language': f"{form_target_lang}"
        }
    
    response = requests.post(URL, data=json.dumps(payload), headers=headers)
    print(response)
    json_data = response.json() #json-to-dict sent to DB
    

# checking if user provided input values properly   
# TODO check non provided source, target or both languages 
    if form_source_lang == form_target_lang:
        return render_template("warning.html", warning = "Source language and target language must be different.") 
    if form_to_translate == "":
        return render_template("warning.html", warning="Please provide the text for translation")

   
    order_number = json_data["order_number"]
    price = json_data["price"]
    source_language = json_data["source_language"]
    status = json_data["status"]
    target_language = json_data["target_language"]
    text = json_data["text"]
    text_format = json_data["text_format"]
    uid = json_data["uid"]

    if response.ok:
        data = Translation_request(order_number,price, source_language, status, target_language, text, text_format, uid)
        db.session.add(data)
        db.session.commit()
        
        # my_query = db.query_all(Translation_request).filter(Translation_request.uid == uid).count()
        # print(my_query)
    

        return render_template("success.html", ok_message="Translation successifuly sent")


if __name__ == '__main__':
    app.run()
