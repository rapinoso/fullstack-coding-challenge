from flask import Flask, redirect, render_template, request, json 
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
# adding it to the app and creating the database on pgAdmin4:
#>>> from app import db
#>>> db.create_all()

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
    translatedText = db.Column(db.Text())
    uid = db.Column(db.String(200), unique=True)

    def __init__(self, order_number, price, source_language, status, target_language, text, text_format, translatedText, uid):
        self.order_number = order_number
        self.price = price
        self.source_language = source_language
        self.status = status
        self.target_language = target_language
        self.text = text
        self.text_format = text_format
        self.translatedText = translatedText 
        self.uid = uid

# variables for the request header
USERNAME = "fullstack-challenge"
API_KEY = "9db71b322d43a6ac0f681784ebdcc6409bb83359"
URL = "https://sandbox.unbabel.com/tapi/v2/translation/"

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'ApiKey {USERNAME}:{API_KEY}'
}

# app routes
@app.route('/', methods=["GET", "POST"])
def index():
    
    list = Translation_request.query.order_by(Translation_request.text)

    return render_template("index.html", list=list)


@app.route('/translate', methods=["GET", "POST"])
def translate():
    
# values are retrieved from form inputs
    form_to_translate = request.form["textToTranslate"]
    form_source_lang = request.form["sourceLanguage"]
    form_target_lang = request.form["targetLanguage"]

# checking if user provided input values properly   
    if form_source_lang == form_target_lang:
        
        list = Translation_request.query.order_by(Translation_request.text)
        return render_template("warning.html", warning = "Source language and target language must be different.", list=list) 
    
    if form_to_translate == "":
        
        list = Translation_request.query.order_by(Translation_request.text)
        return render_template("warning.html", warning="Please provide the text for translation", list=list)

# preparing the json and sending it to translation request endpoint
    post_body = {
        'text': f"{form_to_translate}",
        'source_language': f"{form_source_lang}",
        'target_language': f"{form_target_lang}"
        }

    # post request  
    post_res = requests.post(URL, data=json.dumps(post_body), headers=headers)
    json_data = post_res.json() #json-to-dict sent to DB
    post_uid = json_data["uid"] #putting the value of uid from post response into a variable to make the get request

    # get request
    get_res = requests.get(URL+post_uid, headers=headers)
    get_data = get_res.json()

    order_number = get_data["order_number"]
    price = get_data["price"]
    source_language = get_data["source_language"]
    status = get_data["status"]
    target_language = get_data["target_language"]
    text = get_data["text"]
    text_format = get_data["text_format"]
    translatedText = ""
    uid = get_data["uid"]

    
# TODO check non provided source, target or both languages 
    if post_res.ok:
        data = Translation_request(order_number, price, source_language, status, target_language, text, text_format, translatedText, uid)
        db.session.add(data)
        db.session.commit()
        
        
        list = Translation_request.query.order_by(Translation_request.text)

        return render_template("success.html", ok_message="Translation successifuly sent", list=list)

@app.route("/update", methods=["GET"])
def update():
    
    list = Translation_request.query.all()

    for item in list:
        
        get_res = requests.get(URL+item.uid, headers=headers)
        update = get_res.json()
        
        if 'translatedText' not in update.keys():
            item.translatedText = ""
        else: 
            item.translatedText = update["translatedText"]
            db.session.commit()
    item.status = update["status"]
    db.session.commit()

    list = Translation_request.query.order_by(Translation_request.text) 	
    
    return render_template("index.html", list=list)


if __name__ == '__main__':
    app.run()
