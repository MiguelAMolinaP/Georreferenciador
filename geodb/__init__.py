from flask import Flask
import os




app = Flask(__name__)

UPLOAD_FOLDER = os.path.abspath("./geodb//files/uploads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SECRET_KEY = '6\xf4X\x1e\xb6\xc2>\xac\x92\x85\x01\xcb\xfe\xc4T\xae'
app.config['SECRET_KEY'] = SECRET_KEY
#views
from .views.home import home
from .views.georreferenciar import georreferenciar

#blueprints
app.register_blueprint(home)
app.register_blueprint(georreferenciar)