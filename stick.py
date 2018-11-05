
from flask import Flask, render_template, request, url_for, redirect, make_response, jsonify
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="notoms",
    password="",
    hostname="notoms.mysql.pythonanywhere-services.com",
    databasename="notoms$stick",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class JsonModel(object):
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Note(db.Model, JsonModel):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.Integer)
    title = db.Column(db.String(1024))
    typ = db.Column(db.String(128))
    json = db.Column(db.String(8192))

@app.route("/", methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("noteboard.html")

@app.route('/notes', methods=["GET", "POST"])
def wibble():
    if request.method == "GET":
        if "s" in request.args:
            noteList = Note.query.filter_by(scope=request.args.get('s'))

            return make_response(jsonify({'scope': request.args.get('s'), 'notes': [n.as_dict() for n in noteList]}), 200)
        else:
            return make_response(jsonify({'error': 'Scope (?s=) not defined or not found'}), 404)

    if request.method == "POST":
        if "s" in request.form:
            scope = request.form["s"]

            if "id" in request.form and request.form["id"] is not "":
                note = Note.query.filter_by(id=request.form["id"]).first()
                if note and note.id:
                    if "title" in request.form:
                        note.title = request.form["title"]
                    if "json" in request.form:
                        note.json = request.form["json"]
                    if "scope" in request.form:
                        note.json = request.form["scope"]
                    db.session.commit()

                    return make_response(jsonify({'result': 'OK'}), 200)
                else:
                    return make_response(jsonify({'error': 'Not found'}), 404)
            else:
                note = Note(title=request.form["title"], scope=request.form["scope"], json=request.form["json"], typ=request.form["typ"])
                db.session.add(note)
                db.session.commit()
                return "Created note"

        return request.form["s"]
