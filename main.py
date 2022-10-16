from crypt import methods
from re import RegexFlag
from clarifai_grpc.grpc.api import service_pb2, resources_pb2
from clarifai_grpc.grpc.api.status import status_code_pb2
from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import service_pb2_grpc
from flask import Flask, json, jsonify, render_template, url_for, request, redirect, session, flash
from pymongo import MongoClient
import bcrypt
import requests
import dns.resolver
from bson import ObjectId


dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MyEncoder, self).default(obj)


app = Flask(__name__)
app.json_encoder = MyEncoder
app.secret_key = 'amsdasdjapodj apsdoj paosjd'

cluster = MongoClient(
    "mongodb+srv://BalaAyyappan:bala@nutritionassistant.97pdlqy.mongodb.net/?retryWrites=true&w=majority")

db = cluster.Nutrition_Ass
collection = db.users


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/')
def fyp():
    return render_template('fyp.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = db.collection.users
        username = request.form["username"]

        # check credentials
        login_user = user.find_one({'Name': username})
        if login_user:
            if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['Password']) == login_user['Password']:
                session["username"] = username
                return render_template("window.html")
            else:
                return render_template("login.html", message='Wrong password')
        else:
            return render_template("login.html", message='Invalid username')
    else:
        return render_template("login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        user = db.collection.users
        existing_user = user.find_one(
            {'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(
                request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            user.insert_one(
                {'Name': request.form['username'], 'Password': hashpass, 'City': request.form["city"], 'Gender': request.form["gender"], 'Age': request.form["age"], 'Activity': request.form["activity"],
                    'Height': request.form["height"], 'Weight': request.form["weight"], 'Weight_loss': request.form["Weight_loss"], "Goal": request.form["goal"]})
            session['username'] = request.form['username']
            return redirect(url_for('login'))
        return 'Already a user!'

    return render_template('register.html')

    # "X-RapidAPI-Key": "aa95b88b45mshe4394a422ce8c48p13a698jsn9d8eb019e144",
    #  "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com"


@app.route('/window', methods=['POST', 'GET'])
def window():

  # Calorie Ninja
    url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

    headers = {
        "X-RapidAPI-Key": "aa95b88b45mshe4394a422ce8c48p13a698jsn9d8eb019e144",
        "X-RapidAPI-Host": "calorieninjas.p.rapidapi.com"
    }

    if request.method == 'POST':
        foodname = request.form['foodname']

        querystring = {"query": foodname}
        response = requests.request(
            "GET", url, headers=headers, params=querystring)

        return response.text

    return render_template('window.html')


@app.route('/window', methods=['POST', 'GET'])
def clarifai():
    if request.files.get('image'):
        image = request.files['image'].stream.read()
        stub = service_pb2_grpc.V2Stub(ClarifaiChannel.get_grpc_channel())

        CLARIFAI_API_KEY = "04fe7a95051541789ba44a08eaa5722e"
        APPLICATION_ID = "Nutrition_Assistant1"

        # Authenticate

        # image = '/home/bala/Desktop/Images/foodsample.jpeg'

        metadata = (("authorization", f"Key {CLARIFAI_API_KEY}"),)

        with open(image, "rb") as f:
            file_bytes = f.read()

        request = service_pb2.PostModelOutputsRequest(
            model_id='9504135848be0dd2c39bdab0002f78e9',
            inputs=[
                resources_pb2.Input(
                    data=resources_pb2.Data(
                        image=resources_pb2.Image(
                            base64=file_bytes
                        )
                    )
                )
            ])
        response = stub.PostModelOutputs(request, metadata=metadata)

        if response.status.code != status_code_pb2.SUCCESS:
            raise Exception("Request failed, status code: " +
                            str(response.status.code))

        for concept in response.outputs[0].data.concepts:
            print('%12s: %.2f' % (concept.name, concept.value))

    return render_template('window.html')


if __name__ == "__main__":
    app.run(debug=True)
