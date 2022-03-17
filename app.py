import os
import json
import boto3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv, find_dotenv
from sqlalchemy_utils import database_exists, create_database

load_dotenv(find_dotenv())

app = Flask(__name__)
database_url: str

MYSQL_FORMAT = 'mysql://{}:{}@{}/{}'

if os.environ['ENV'] == 'prod':
    session = boto3.Session(aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))

    client = session.client(service_name='secretsmanager', region_name=os.getenv('AWS_REGION'))
    response = client.get_secret_value(SecretId=os.getenv('SECRET_ID'))
    database_secrets = json.loads(response['SecretString'])

    database_url = MYSQL_FORMAT.format(database_secrets['DB_USERNAME'],
                                       database_secrets['DB_PASSWORD'],
                                       database_secrets['DB_HOST'],
                                       database_secrets['DB_NAME'])

else:
    database_url = MYSQL_FORMAT.format(os.getenv('DB_USERNAME'),
                                       os.getenv('DB_PASSWORD'),
                                       os.getenv('DB_HOST'),
                                       os.getenv('DB_NAME'))

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if not database_exists(database_url):
    create_database(database_url)

db = SQLAlchemy(app)
db.init_app(app)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    banner = db.Column(db.String(20))
    db.UniqueConstraint(banner)

    def __init__(self, first_name, last_name, banner):
        self.first_name = first_name
        self.last_name = last_name
        self.banner = banner

    def serialize(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'banner': self.banner
        }


db.create_all()


@app.route("/storestudents", methods=['POST'])
def store():
    data = request.get_json(force=True)
    students = data.get("students")
    if len(students) > 0:
        try:
            for student in students:
                student_row = Student(first_name=student.get("first_name"),
                                      last_name=student.get("last_name"),
                                      banner=student.get("banner"))
                db.session.add(student_row)
            db.session.commit()
            return {'success': True}, 200
        except Exception as e:
            return {'error': str(e.orig)}, 400
    else:
        return {'error': "students array is empty"}, 400


@app.route("/liststudents", methods=['GET'])
def retrieve():
    students = Student.query.all()
    student_list = [Student.serialize(user) for user in students]
    if request.headers.get("Content-Type") == 'application/json':
        return jsonify(student_list)
    else:
        return render_template('student_list.html', data=student_list)


if __name__ == "__main__":
    app.run(debug=True)
