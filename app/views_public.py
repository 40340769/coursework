from flask import Blueprint, render_template, flash, request, session, redirect, url_for
from . import requires_login
import sqlite3
import bcrypt
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

db_location = 'app/var/strainer.db'
views_public = Blueprint('views_public', __name__)

# Pages that are available publicly (users don't need to be logged in):

###################################################################

# Home page
@views_public.route('/', methods=['GET','POST'])
def home():
	# Displaying Home page
	return render_template("public/home.html")

###################################################################

# About page
@views_public.route('/about', methods=['GET','POST'])
def about():
	# Displaying About page
	return render_template("public/about.html")

###################################################################

# Login page
@views_public.route('/login', methods=['GET','POST'])
def login():
	# User clicked "LOGIN" button
	if request.method == 'POST':
		# Collecting data entered by the user
		email = request.form.get('email')
		password = request.form.get('password')
		# Connecting to the database
		conn = sqlite3.connect(db_location)
		cursor = conn.cursor()
		# Checking if the user (email) already exists
		query = "SELECT * FROM users WHERE email=?"
		cursor.execute(query,(email,))
		user = cursor.fetchall()
		if user == []:
			# User (email) doesn't exists
			flash('Wrong email or password. Please try again.', category='error')
		else:
			# User (email) exists
			email_db = user[0][1]
			password_db = user[0][4]
			if(email_db == email and password_db == bcrypt.hashpw(password.encode('utf-8'),password_db)):
				# User (email) and email match the values from the database
				session['logged'] = True
				session['email'] = email
				# Redirecting to My Bookmarks page
				return redirect(url_for('views_auth.my_bookmarks'))
			else:
				# User (email) and email don't match the values from the database
				flash('Wrong email or password. Please try again', category='error')
	
	# Displaying Login page with empty form
	return render_template("public/login.html")

###################################################################

# Register page
@views_public.route('/register', methods=['GET','POST'])
def register():
	# User clicked "REGISTER" button
	if request.method == 'POST':
		# Collecting data entered by the user
		email = request.form.get('email')
		first_name = request.form.get('firstName')
		last_name = request.form.get('lastName')
		password1 = request.form.get('password1')
		password2 = request.form.get('password2')
		password_hashed = bcrypt.hashpw(password1.encode('utf-8'),bcrypt.gensalt())
		
		# Checking if user entered required data (length) in the form fields
		if len(email) < 4:
			flash('Email must be greater than 3 characters.', category='error')
		elif len(first_name) < 2:
			flash('First name must be greater than 1 character.', category='error') 
		elif len(last_name) < 2:
			flash('Last name must be greater than 1 character.', category='error')
		elif len(password1) < 7:
			flash('Password must be greater than 6 characters.', category='error')
		elif password1 != password2:
			flash('Passwords don\'t match.', category='error')
		else:
			# Connecting to the database
			conn = sqlite3.connect(db_location)
			cursor = conn.cursor()
			# Checking if the user (email) already exists
			query = "SELECT * FROM users WHERE email=?"
			cursor.execute(query,(email,))
			user = cursor.fetchall()
			if user != []:
				# User (email) already exists
				flash('Email already exists. Try a different email.', category='error')
			else:	
				# User (email) is available
				# Adding new user to the database
				conn = sqlite3.connect(db_location)
				cursor = conn.cursor()
				query = "INSERT INTO users (email,first_name,last_name,h_password) VALUES (?,?,?,?)"
				cursor.execute(query,(email,first_name,last_name,password_hashed))
				conn.commit()
				conn.close()
				flash('Account created successfully!', category='success')
				session['logged'] = True
				session['email'] = email
				# Redirecting to My Bookmarks page
				return redirect(url_for('views_auth.my_bookmarks'))
	
	# Displaying Register page with empty form
	return render_template("public/register.html")

###################################################################

# Contact page
# Strainer email addresses:
# 	contact.strainer.now@gmail.com 	- "backstage" email used to automatically send emails
# 	contact.strainer.main@gmail.com - "admin" email used to read and reply users' messages
@views_public.route('/contact', methods=['GET','POST'])
def contact():
	# User clicked "SEND" button
	if request.method == 'POST':
		# Collecting data entered by the user
		first_name = request.form.get('firstName')
		last_name = request.form.get('lastName')
		email = request.form.get('email')
		message = request.form.get('message')
		
		# Checking if user entered required data (length) in the form fields
		if len(first_name) < 2:
			flash('First name must be greater than 1 character.', category='error')
		elif len(last_name) < 2:
			flash('Last name must be greater than 1 character.', category='error') 
		elif len(email) < 4:
			flash('Email must be greater than 3 characters.', category='error')
		elif len(message) < 2:
			flash('Message must be greater than 1 character.', category='error')
		else:
			# Sending confirmation email to the user
			# Formating email
			msg_user = EmailMessage()
			msg_user['Subject'] = "Contact message - Strainer"
			msg_user['From'] = "contact.strainer.now@gmail.com"
			msg_user['To'] = email
			msg_user.set_content('Thank you for sending us a message. We will respond within 24 hours. Strainer Team.')
			image_cid = make_msgid()
			msg_user.add_alternative("""<!DOCTYPE html>
				<html>
					<body>
						<p>Hello """ + first_name + """,</p>
						<p>Thank you for sending us a message.</p>
						<p>We will respond within 24 hours.</p>
						<p><b>Strainer Team</b></p>
						<br />
						<p style="text-align:center"><img src=\"cid:{image_cid}\" width="100" height="auto" /></p>
					</body>
				</html>
				""".format(image_cid=image_cid[1:-1]), subtype='html')
			# Adding Strainer logo to the confirmation email
			with open('app/static/images/logo_email.png', 'rb') as img:
				maintype, subtype = mimetypes.guess_type(img.name)[0].split('/')
				msg_user.get_payload()[1].add_related(img.read(), maintype=maintype, subtype=subtype, cid=image_cid)
			# Sending email
			with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp_user:
				smtp_user.login("contact.strainer.now@gmail.com","strainer123")
				smtp_user.send_message(msg_user)

			# Sending notification email to Strainer admin
			# Formating email
			msg_strainer = EmailMessage()
			msg_strainer['Subject'] = "Contact message - Strainer"
			msg_strainer['From'] = "contact.strainer.now@gmail.com"
			msg_strainer['To'] = "contact.strainer.main@gmail.com"
			msg_strainer.set_content('You have received the following message from the Strainer user: \nUser: ' + first_name + ' ' + last_name + '\nEmail: ' + email + '\nMessage: ' + message)
			msg_strainer.add_alternative("""<!DOCTYPE html>
				<html>
					<body>
						<p>You have received the following message from the Strainer user:</p>
						<p>User: """ + first_name + " " + last_name + """</p>
						<p>Email: """ + email + """</p>
						<p>Message: """ + message + """</p>
					</body>
				</html>
				""", subtype='html')
			# Sending email
			with smtplib.SMTP_SSL('smtp.gmail.com',465) as smtp_strainer:
				smtp_strainer.login("contact.strainer.now@gmail.com","strainer123")
				smtp_strainer.send_message(msg_strainer)

			flash('Your message has been successfully sent!', category='success')
			# Reloading Contact page with displayed confirmation message
			return redirect(url_for('views_public.contact'))
	
	# Displaying Contact page with empty form
	return render_template("public/contact.html")

###################################################################

@views_public.route('/privacy', methods=['GET','POST'])
def privacy():
	# Displaying Privacy page
	return render_template("public/privacy.html")
