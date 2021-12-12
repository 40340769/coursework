from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from . import requires_login
import sqlite3
import bcrypt

db_location = 'app/var/strainer.db'
views_auth = Blueprint('views_auth', __name__)