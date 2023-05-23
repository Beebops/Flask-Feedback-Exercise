from flask import Flask, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, UserLoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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

# ---- User Routes -------

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

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Deletes a user and their associated feedback"""
    print(f' ***** {username} ******')
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')

    if username != session['username']:       
        flash("You don't have permission to do that!", "danger")
        return redirect('/')

    try:
        user = User.query.get_or_404(username)

        # Delete the associated feedback using cascading deletion
        db.session.delete(user)

        db.session.commit()
        flash("User and associated feedback deleted!", "info")
        return redirect('/')
    except SQLAlchemyError:
        db.session.rollback()
        flash("An error occurred while deleting the user and associated feedback.", "danger")
        return redirect('/')    


@app.route('/users/<username>')
def show_secret(username):
    """Shows the logged in User's secret information"""
    if "username" not in session or username != session['username']:
        flash("Please login first!", "danger")
        return redirect('/')
    user = User.query.get_or_404(username)
    all_feedback = Feedback.query.all()
    return render_template('secret.html', user=user, all_feedback=all_feedback)
          
# ---- Feedback Routes -------
@app.route('/users/<username>/feedback/add')
def show_feedback_form(username):
    """Show feedback form to logged in User"""
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    return render_template('feedback_form.html', user=user, form=form)

@app.route('/users/<username>/feedback/add', methods=['POST'])
def submit_feedback(username):
    """Handles logged in User's feedback form submit"""
    if "username" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(f'/users/{username}')

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Deletes the selected feedback of the logged in User"""
    if 'username' not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback deleted!", "info")
        return redirect(f'/users/{feedback.username}')
    except SQLAlchemyError:    
        db.session.rollback()
        flash("An error occurred while deleting the feedback.", "danger")
        return redirect('/')

    


if __name__ == '__main__':
    app.run(debug=True)
