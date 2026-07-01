import sqlite3
from datetime import datetime

def get_connection():
    conn = sqlite3.connect("database.db")