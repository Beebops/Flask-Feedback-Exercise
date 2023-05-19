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
#db.create_all()

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
            session['user_id'] = user.id
            return redirect('/secret')
        else:
            form.username.errors = ['Please enter a valid username and password']
    return render_template('login_form.html', form=form)        

@app.route('/logout', methods=['POST'])
def logout_user():
    """Logs out user and removes user from session"""
    session.pop('user_id')
    flash('Goodbye!', 'info')
    return redirect('/login')

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
        session['user_id'] = new_user.id
        flash(f"Welcome, {new_user.first_name}! Your account has been created!", 'success')
        return redirect('/secret')
    
    return render_template('register_form.html', form=form)

@app.route('/secret')
def show_secret():
    return render_template('secret.html')
          



if __name__ == '__main__':
    app.run(debug=True)
