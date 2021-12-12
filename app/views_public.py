from flask import Blueprint, render_template, flash, request, session, redirect, url_for
from . import requires_login
import sqlite3

db_location = 'app/var/strainer.db'
views_public = Blueprint('views_public', __name__)

@views_public.route('/', methods=['GET','POST'])
def home():
	return render_template("public/home.html")
