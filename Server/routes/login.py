from flask import Blueprint, render_template
import sqlite3
from config import *


principal = Blueprint('list', __name__)


@principal.route('/')
def index():
    return render_template('index.html')