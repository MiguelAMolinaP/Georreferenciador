from flask import Blueprint
from flask import render_template, url_for

home = Blueprint('home', __name__)

@home.route('/')
@home.route('/home')
def home_page():
    return render_template('home.html')

