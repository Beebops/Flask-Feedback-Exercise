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
          



if __name__ == '__main__':
    app.run(debug=True)
