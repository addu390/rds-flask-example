import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv, find_dotenv
from sqlalchemy_utils import database_exists, create_database

load_dotenv(find_dotenv())

app = Flask(__name__)
database_url: str

if os.environ['ENV'] == 'prod':
    # Retrieve from AWS Secrets Manager
    database_url = ""
else:
    database_url = 'mysql://{}:{}@{}/{}'.format(os.getenv('DB_USERNAME'),
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
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    banner = db.Column(db.String(50))
    db.UniqueConstraint(banner)

    def __init__(self, first_name, last_name, banner):
        self.first_name = first_name
        self.last_name = last_name
        self.banner = banner


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


if __name__ == "__main__":
    app.run(debug=True)
