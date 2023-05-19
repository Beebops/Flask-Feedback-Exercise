from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User
from forms import RegisterForm, UserLoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mylittlesecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback_db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


toolbar = DebugToolbarExtension(app)

connect_db(app)

app.app_context().push()

@app.route('/')
def index():
    """Redirects to registration form"""
    return redirect('/register')

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """Form to handle user login"""
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.first_name}!", 'success')
            session['username'] = user.username
            return redirect(f'/users/{username}')
        else:
            form.username.errors = ['Please enter a valid username and password']
    return render_template('login_form.html', form=form)        

@app.route('/logout')
def logout_user():
    """Logs out user and removes user from session"""
    session.pop('username')
    flash('Goodbye!', 'info')
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    """Form to handle new user registration"""
    form = RegisterForm()
    if form.validate_on_submit():
        data = {k: v for k, v in form.data.items() if k != "csrf_token"}
        new_user = User.register(**data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Uh-oh! That username is taken. Please pick another')
            return render_template('register_form.html', form=form)
        session['username'] = new_user.username
        flash(f"Welcome, {new_user.first_name}! Your account has been created!", 'success')
        return redirect(f'/users/{new_user.username}')
    
    return render_template('register_form.html', form=form)

@app.route('/users/<username>')
def show_secret(username):
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    user = User.query.get_or_404(username)
    return render_template('secret.html', user=user)
          



if __name__ == '__main__':
    app.run(debug=True)
