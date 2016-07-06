from flask import Flask
app = Flask(__name__)
from flaskexample import views2
app._static_folder = '/root/Hosting/flaskexample/static'
