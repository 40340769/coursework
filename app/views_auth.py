from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import requires_login
import sqlite3
import bcrypt

db_location = 'app/var/strainer.db'
views_auth = Blueprint('views_auth', __name__)

# Pages that are available only for the users that are logged in:

###################################################################

# Logout page
@views_auth.route('/logout', methods=['GET','POST'])
@requires_login
def logout():
	# Removing data from session
	session.pop('logged',None)
	session.pop('email',None)
	session.pop('user_id',None)
	# Redirecting to Home page
	return redirect(url_for('views_public.home'))

###################################################################

# My Bookmarks page
@views_auth.route('/my-bookmarks', methods=['GET','POST'])
@requires_login
def my_bookmarks():
	# Connecting to the database
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	# Collecting all the data regarding particular user
	query_user = "SELECT * FROM users WHERE email=?"
	cursor.execute(query_user,(session['email'],))
	user_info = cursor.fetchall()
	if user_info == []:
		# No user found in the database
		pass 
	else:	
		# User found in the database
		session['user_id'] = user_info[0][0]
		user_id = user_info[0][0]
	user_id = session['user_id']

	# User clicked "SEARCH" button
	if request.form.get('search_bookmark') == 'search_bookmark':
		search_term = request.form.get('search_term')
		# Connecting to the database
		conn = sqlite3.connect(db_location)
		cursor = conn.cursor()
		# Collecting all the data that include a search term entered by the user
		query_search = "SELECT * FROM bookmarks WHERE ((name LIKE ?) OR (category LIKE ?) OR (url LIKE ?) OR (notes LIKE ?)) AND user_id=? ORDER BY name";
		cursor.execute(query_search,(f"%{search_term}%",f"%{search_term}%",f"%{search_term}%",f"%{search_term}%",user_id))
		user_bookmarks_search = cursor.fetchall()
		conn.close()
		if user_bookmarks_search == []:
			# No bookmarks with a given search term found
			user_bookmarks = user_bookmarks_search
			flash('Sorry, no specified bookmarks found. Please try again.', category='search_error')
		else:
			# Bookmarks with a given search term found
			user_bookmarks = user_bookmarks_search
			flash('Result(s) for: "' + search_term + '"', category='search_success')
	# User clicked "SEARCH ALL" button
	elif request.form.get('show_all_bookmarks') == 'show_all_bookmarks':
		# Collecting all the data regarding the bookmarks of particular user
		query_bookmarks = "SELECT * FROM bookmarks WHERE user_id=? ORDER BY name"
		cursor.execute(query_bookmarks,(user_id,))
		user_bookmarks = cursor.fetchall()
		conn.close()
	# User accessed My Bookmarks page via link
	else:
		# Collecting all the data regarding the bookmarks of particular user
		query_bookmarks = "SELECT * FROM bookmarks WHERE user_id=? ORDER BY name"
		cursor.execute(query_bookmarks,(user_id,))
		user_bookmarks = cursor.fetchall()
		conn.close()

	# User clicked "VIEW" button
	if request.form.get('view_bookmark') == 'view_bookmark':
		bookmark_id = request.form.get('hidden_bookmark_id')
		session['bookmark_id'] = bookmark_id
		# Redirecting to View Bookmark page
		return redirect(url_for('views_auth.view_bookmark'))

	# User clicked "EDIT" button
	if request.form.get('edit_bookmark') == 'edit_bookmark':
		bookmark_id = request.form.get('hidden_bookmark_id')
		session['bookmark_id'] = bookmark_id
		# Redirecting to Edit Bookmark page
		return redirect(url_for('views_auth.edit_bookmark'))

	# User clicked "DELETE" button
	if request.form.get('delete_bookmark') == 'delete_bookmark':
		bookmark_id = request.form.get('hidden_bookmark_id')
		session['bookmark_id'] = bookmark_id
		# Redirecting to Delete Bookmark page
		return redirect(url_for('views_auth.delete_bookmark'))

	# Displaying My Bookmarks page with all bookmarks of particular user
	return render_template("auth/my_bookmarks.html", user_bookmarks=user_bookmarks)

###################################################################

# Account page
@views_auth.route('/account', methods=['GET','POST'])
@requires_login
def account():
	# Connecting to the database
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	# Collecting all the data regarding particular user
	query_user = "SELECT * FROM users WHERE email=?"
	cursor.execute(query_user,(session['email'],))
	user_info = cursor.fetchall()
	conn.close()

	# Displaying Account page with all details of particular user
	return render_template("auth/account.html", user_info=user_info)

###################################################################

# New Bookmark page
@views_auth.route('/new-bookmark', methods=['GET','POST'])
@requires_login
def new_bookmark():
	# Connecting to the database
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	# Collecting all the data regarding particular user
	query_user = "SELECT * FROM users WHERE email=?"
	cursor.execute(query_user,(session['email'],))
	user_info = cursor.fetchall()
	if user_info == []:
		# No user found in the database
		pass 
	else:	
		# User found in the database
		session['user_id'] = user_info[0][0]
		user_id = user_info[0][0]
	conn.close()

	# User clicked "ADD" button
	if request.method == 'POST':
		# Collecting data regarding a new bookmark entered by the user
		name = request.form.get('name')
		category = request.form.get('category')
		url = request.form.get('url')
		note = request.form.get('note')

		# Checking if user entered required data (length) in the form fields 
		if len(name) < 1:
			flash('Name of the bookmark cannot be empty.', category='error')
		elif len(category) < 1:
			flash('Category of the bookmark cannot be empty.', category='error')
		elif len(url) < 1:
			flash('URL of the bookmark cannot be empty.', category='error')
		elif len(note) < 1:
			flash('Note for the bookmark cannot be empty.', category='error')
		else:
			# Adding new bookmark to database
			conn = sqlite3.connect(db_location)
			cursor = conn.cursor()
			query = "INSERT INTO bookmarks (name,category,url,notes,user_id) VALUES (?,?,?,?,?)"
			cursor.execute(query,(name,category,url,note,user_id))
			conn.commit()
			conn.close()
			flash('Bookmark added!', category='success')
			# Redirecting to My Bookmarks page
			return redirect(url_for('views_auth.my_bookmarks'))

	# Displaying New Bookmark page with empty form
	return render_template("auth/new_bookmark.html")

###################################################################

# View Bookmark page
@views_auth.route('/view-bookmark', methods=['GET','POST'])
@requires_login
def view_bookmark():
	bookmark_id = session['bookmark_id']
	session.pop('bookmark_id',None)
	# Connecting to the database
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	# Collecting all the data regarding particular bookmark
	query_bookmark = "SELECT * FROM bookmarks WHERE bookmark_id=?"
	cursor.execute(query_bookmark,(bookmark_id,))
	bookmark_info = cursor.fetchall()
	conn.close()

	# Displaying View Bookmark page with all details of particular bookmark
	return render_template("auth/view_bookmark.html", bookmark_info=bookmark_info)

###################################################################

# Delete Bookmark page
@views_auth.route('/delete-bookmark', methods=['GET','POST'])
@requires_login
def delete_bookmark():
	# User clicked "YES" button (wants to delete particular bookmark)
	if request.form.get('delete_bookmark_yes') == 'delete_bookmark_yes':
		bookmark_id = request.form.get('hidden_bookmark_id')
		# Connecting to the database
		conn = sqlite3.connect(db_location)
		cursor = conn.cursor()
		# Removing particular bookmark from database
		query_bookmark = "DELETE FROM bookmarks WHERE bookmark_id=?"
		cursor.execute(query_bookmark,(bookmark_id,))
		conn.commit()
		conn.close()
		flash('Bookmark deleted!', category='success')

		# Redirecting to My Bookmarks page
		return redirect(url_for('views_auth.my_bookmarks'))

	bookmark_id = session['bookmark_id']
	session.pop('bookmark_id',None)
	# Connecting to the database
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	# Collecting all the data regarding particular bookmark
	query_bookmark = "SELECT * FROM bookmarks WHERE bookmark_id=?"
	cursor.execute(query_bookmark,(bookmark_id,))
	bookmark_info = cursor.fetchall()
	conn.close()

	# Displaying Delete Bookmarks page with all details of particular bookmark
	return render_template("auth/delete_bookmark.html", bookmark_info=bookmark_info)

###################################################################

# Edit Bookmark page
@views_auth.route('/edit-bookmark', methods=['GET','POST'])
@requires_login
def edit_bookmark():
	# User clicked "EDIT" button
	if request.method == 'POST':
		# Collecting data regarding a edited bookmark entered by the user
		bookmark_id = request.form.get('hidden_bookmark_id')
		bookmark_name = request.form.get('name')
		bookmark_category = request.form.get('category')
		bookmark_url = request.form.get('url')
		bookmark_note = request.form.get('note')

		# Checking if user entered required data (length) in the form fields
		if len(bookmark_name) < 1:
			flash('Name of the bookmark cannot be empty.', category='error')
		elif len(bookmark_category) < 1:
			flash('Category of the bookmark cannot be empty.', category='error')
		elif len(bookmark_url) < 1:
			flash('URL of the bookmark cannot be empty.', category='error')
		elif len(bookmark_note) < 1:
			flash('Note for the bookmark cannot be empty.', category='error')
		else:
			# Updating bookmark in the database
			conn = sqlite3.connect(db_location)
			cursor = conn.cursor()
			query_bookmark = "UPDATE bookmarks SET name=?,category=?,url=?,notes=? WHERE bookmark_id=?"
			cursor.execute(query_bookmark,(bookmark_name,bookmark_category,bookmark_url,bookmark_note,bookmark_id))
			conn.commit()
			conn.close()
			flash('Bookmark updated!', category='success')
			# Redirecting to My Bookmarks page
			return redirect(url_for('views_auth.my_bookmarks'))

		session['bookmark_id'] = bookmark_id
		# Reloading Edit Bookmark page with displayed error message
		return redirect(url_for('views_auth.edit_bookmark'))

	bookmark_id = session['bookmark_id']
	session.pop('bookmark_id',None)
	# Connecting to the database
	conn = sqlite3.connect(db_location)
	cursor = conn.cursor()
	# Collecting all the data regarding particular bookmark
	query_bookmark = "SELECT * FROM bookmarks WHERE bookmark_id=?"
	cursor.execute(query_bookmark,(bookmark_id,))
	bookmark_info = cursor.fetchall()
	conn.close()

	# Displaying Edit Bookmark page with all details of particular bookmark
	return render_template("auth/edit_bookmark.html", bookmark_info=bookmark_info)
