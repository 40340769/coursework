from flask import Flask, session, redirect, url_for
from functools import wraps
from os import urandom
from base64 import b64encode 
import sqlite3

db_location = 'app/var/strainer.db'

def create_app():
	app = Flask(__name__)
	
	secret_key_bin = urandom(24)
	secret_key_str = b64encode(secret_key_bin).decode('utf-8')
	app.config['SECRET_KEY'] = secret_key_str
	app.config['DEBUG'] = True
	app.config['ENV'] = 'development'

	from .views_public import views_public
	from .views_auth import views_auth

	app.register_blueprint(views_public, url_prefix='/')
	app.register_blueprint(views_auth, url_prefix='/')

	return app

def create_db_users():
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS users 
		(user_id INTEGER PRIMARY KEY AUTOINCREMENT,
		email TEXT,
		first_name TEXT,
		last_name TEXT,
		h_password TEXT)
	""")
	conn.commit()
	conn.close()

def create_db_bookmarks():
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS bookmarks 
		(bookmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
		name TEXT,
		category TEXT,
		url TEXT,
		notes TEXT,
		user_id INTEGER,
		FOREIGN KEY(user_id) REFERENCES users(user_id))
	""")
	conn.commit()
	conn.close()

def requires_login(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        status = session.get('logged',False)
        if not status:
            return redirect(url_for('views_public.login'))
        return f(*args,**kwargs)
    return decorated
