import bcrypt
from utils.db import get_db

def hash_pw(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def check_pw(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed)

def signup(username, password):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username,password) VALUES (?,?)",
            (username, hash_pw(password))
        )
        db.commit()
        return True
    except:
        return False

def login(username, password):
    db = get_db()
    user = db.execute(
        "SELECT id,password FROM users WHERE username=?",
        (username,)
    ).fetchone()

    if user and check_pw(password, user[1]):
        return user[0]
    return None
