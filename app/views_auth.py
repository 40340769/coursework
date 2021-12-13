from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import requires_login
import sqlite3
import bcrypt

db_location = 'app/var/strainer.db'
views_auth = Blueprint('views_auth', __name__)

@views_auth.route('/logout', methods=['GET','POST'])
@requires_login
def logout():
	session.pop('logged',None)
	session.pop('email',None)
	session.pop('user_id',None)
	return redirect(url_for('views_public.home'))

@views_auth.route('/my-bookmarks', methods=['GET','POST'])
@requires_login
def my_bookmarks():
	return render_template("auth/my_bookmarks.html")

@views_auth.route('/account', methods=['GET','POST'])
@requires_login
def account():
	return render_template("auth/account.html")

@views_auth.route('/new-bookmark', methods=['GET','POST'])
@requires_login
def new_bookmark():
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()

	query_user = "SELECT * FROM users WHERE email=?"
	cursor.execute(query_user,(session['email'],))
	user_info = cursor.fetchall()
	if user_info == []:
		pass 
	else:	
		session['user_id'] = user_info[0][0]
		user_id = user_info[0][0]
	conn.close()

	if request.method == 'POST':
		name = request.form.get('name')
		category = request.form.get('category')
		url = request.form.get('url')
		note = request.form.get('note')

		if len(name) < 1:
			flash('Name of the bookmark is too short!', category='error')
		elif len(category) < 1:
			flash('Category of the bookmark is too short!', category='error')
		elif len(url) < 1:
			flash('URL of the bookmark is too short!', category='error')
		elif len(note) < 1:
			flash('Note for the bookmark is too short!', category='error')
		else:
			# Add bookmark to database
			conn = sqlite3.connect(db_location)
			cursor = conn.cursor()
			query = "INSERT INTO bookmarks (name,category,url,notes,user_id) VALUES (?,?,?,?,?)"
			cursor.execute(query,(name,category,url,note,user_id))
			conn.commit()
			conn.close()
			flash('Bookmark added!', category='success')
			return redirect(url_for('views_auth.my_bookmarks'))

	return render_template("auth/new_bookmark.html")