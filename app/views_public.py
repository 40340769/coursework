from flask import Blueprint, render_template, flash, request, session, redirect, url_for
from . import requires_login
import sqlite3

db_location = 'app/var/strainer.db'
views_public = Blueprint('views_public', __name__)

@views_public.route('/', methods=['GET','POST'])
def home():
	return render_template("public/home.html")

@views_public.route('/about', methods=['GET','POST'])
def about():
	return render_template("public/about.html")

@views_public.route('/login', methods=['GET','POST'])
def login():
	return render_template("public/login.html")

@views_public.route('/register', methods=['GET','POST'])
def register():
	return render_template("public/register.html")

@views_public.route('/contact', methods=['GET','POST'])
def contact():
	return render_template("public/contact.html")

@views_public.route('/privacy', methods=['GET','POST'])
def privacy():
	return render_template("public/privacy.html")
