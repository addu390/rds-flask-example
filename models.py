# from app import app
# from flask_sqlalchemy import SQLAlchemy
#
# db = SQLAlchemy(app)
#
#
# class Student(db.Model):
#     __tablename__ = 'students'
#     id = db.Column(db.Integer, primary_key=True)
#     first_name = db.Column(db.String(100))
#     last_name = db.Column(db.String(100))
#     banner = db.Column(db.String(20))
#     db.UniqueConstraint(banner)
#
#     def __init__(self, first_name, last_name, banner):
#         self.first_name = first_name
#         self.last_name = last_name
#         self.banner = banner
#
#     def serialize(self):
#         return {
#             'first_name': self.first_name,
#             'last_name': self.last_name,
#             'banner': self.banner
#         }