from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['SECRET_KEY'] = 'VERYVERYSECRETKEY'
app.config['TWITCH_CLIENT_ID'] = '95asuy3jl29tye4odxmykelgawgot6'

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:booksami@localhost:6000/twitchclips'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://gktfyoeiqavwow:6dd7085870301b2f2f8fff9cd366a9a91ad140279a4f93692a6eccec631a9070@ec2-52-70-15-120.compute-1.amazonaws.com:5432/d30atughl0endi'

db = SQLAlchemy(app)

from twitchclips import routes  # nopep8
