from flask import Flask
from flaskext.mysql import MySQL
import uuid

app = Flask(__name__)
mysql = MySQL()

app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'flask'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

from game import views