from flask import render_template
from . import main  # Blueprint import

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')