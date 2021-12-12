from app import create_app, create_db_users, create_db_bookmarks

app = create_app()

create_db_users()
create_db_bookmarks()

if __name__ == '__main__':
	app.run()