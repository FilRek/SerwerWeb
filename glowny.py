from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user

app = Flask(__name__)

db = SQLAlchemy()
DB_NAME = "database.db"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
@app.route("/")
def str_glowna():
    return render_template("index.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Błędne hasło.', category='error')
        else:
            flash('Podany email nie istnieje.', category='error')

    return render_template("login.html", user=current_user)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@app.route("/signup")
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('Name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email już istnieje.', category='error')
        elif len(email) < 4:
            flash('Email musi być dłuższy niż 3 znaki', category='error')
        elif len(name) < 2:
            flash('Nazwa użytkownika musi byc dłuższa niż jeden znak', category='error')
        elif password1 != password2:
            flash('Hasła nie są takie same', category='error')
        elif len(password1) < 7:
            flash('Hasło musi mieć co najmniej 7 znaków.', category='error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)


if __name__ == "__main__":
    app.run(debug=True)