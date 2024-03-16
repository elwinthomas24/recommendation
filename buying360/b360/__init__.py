from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.static_folder = 'static'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appDB.db'

app.config['SECRET_KEY'] = 'd5389b17efe159e5278a52e1'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"
from b360 import routes

with app.app_context():
    db.create_all()



# @app.route('/about/<username>') #dynamic route
# def about_page(username):
#     return f'<h1>this is about of {username}</h1>'