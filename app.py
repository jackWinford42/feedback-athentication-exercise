"""Feedback Application"""

from flask import Flask, render_template, redirect, request, session
from models import db, connect_db, User, Feedback
from forms import register, login, feedback
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "thisIsSecret"

connect_db(app)
# print(Feedback.query.delete())
# print(User.query.delete())
# db.session.commit()
db.create_all()

@app.route('/')
def redirect_to_register():
    """root route redirects to register route"""

    return redirect('/register')

@app.route('/register', methods = ['POST', 'GET'])
def register_user():
    """display the register_user.html page with a form for registering a user"""
    
    form = register()
    # print(User.query.all())
    # print(User.query.delete())
    # db.session.commit()
    if request.method == 'GET':
        return render_template('register.html',
                                title='Register an Account',
                                form=form)
    else:

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.username
        
        return redirect(f'/users/{username}')

@app.route('/login', methods = ['POST', 'GET'])
def login_user():
    """display a form to login a user and process that form"""

    login_form = login()

    if request.method == 'GET':

        return render_template('login.html',
                                title='login',
                                form=login_form)
    else:

        username = login_form.username.data
        password = login_form.password.data

        if User.authenticate(username, password):

            user = User.query.filter_by(username=username).first()
            print(user)
            session["user_id"] = user.username

            return redirect(f'/users/{username}')
        else:
            return redirect('/login')

@app.route('/users/<username>')
def user_page(username):
    """display an html page with information about the chosen user"""

    if "user_id" not in session:
        raise Unauthorized()
    elif session["user_id"] is None:
        return render_template('base.html',
                                title="User Has Been Deleted")
    else:

        user = User.query.filter_by(username=username).first()
        feedback_list = Feedback.query.filter_by(username=username)

        title = f"User page for {user.first_name} {user.last_name}"

        return render_template('user.html',
                                user=user,
                                title=title,
                                feedback_list=feedback_list)

@app.route('/logout')
def clear_session():
    """clear any information from the session and redirect to root"""

    session.clear()
    return redirect('/')

@app.route('/users/<username>/delete', methods = ['POST'])
def delete_user(username):
    """delete a user"""
    if "user_id" not in session:
        raise Unauthorized()
    else:
        user = User.query.filter_by(username=username).first()
        feedback_list = Feedback.query.filter_by(username=username)

        for feedback in feedback_list:
            db.session.delete(feedback)

        db.session.delete(user)
        db.session.commit()

        session["user_id"] = None

        return redirect('/')

@app.route('/users/<username>/feedback/add', methods = ['POST', 'GET'])
def add_feedback(username):
    """display a form to add feedback and process the form on submission"""

    feedback_form = feedback()

    if request.method == 'GET':
        if "user_id" not in session:
            raise Unauthorized()
        elif session["user_id"] is None:
            return render_template('base.html',
                                    title="User Has Been Deleted")
        else:
            url = f'/users/{username}/feedback/add'
            action = "Submit"
            return render_template('feedback.html',
                                    title='Feedback',
                                    form=feedback_form,
                                    url=url,
                                    action=action)
    else:
        
        feedback_data = Feedback(
            title = feedback_form.title.data,
            content = feedback_form.content.data,
            username = username
        )

        db.session.add(feedback_data)
        db.session.commit()

        return redirect(f'/users/{username}')

@app.route('/feedback/<feedback_id>/update', methods = ['POST', 'GET'])
def update_feedback(feedback_id):
    """display a form to edit existing feedback if the editing user is also the 
    posting user. On POST update the feedback table and redirect to users/<username>"""

    feedback_form = feedback()

    if "user_id" not in session:
        raise Unauthorized()
    elif session["user_id"] is None:
        return render_template('base.html',
                                title="User Has Been Deleted")
    else:
        if request.method == 'GET':
            
            url = f'/feedback/{feedback_id}/update'
            action = "Update"
            return render_template('feedback.html',
                                    title='Provide Updated Feedback',
                                    form=feedback_form,
                                    url=url,
                                    action=action)
        else:
            
            updated_feedback = Feedback.query.get_or_404(feedback_id)

            updated_feedback.title = feedback_form.title.data
            updated_feedback.content = feedback_form.content.data

            db.session.add(updated_feedback)
            db.session.commit()

            return redirect(f'/users/{updated_feedback.username}')

@app.route('/feedback/<feedback_id>/delete', methods = ['POST'])
def delete_feedback(feedback_id):
    """delete a row from the feedback table based on the query id then redirect"""
    
    to_be_deleted = Feedback.query.get_or_404(feedback_id)
    username = to_be_deleted.username

    if "user_id" not in session:

        raise Unauthorized()
    elif session["user_id"] != username:

        return render_template('base.html',
                        title="You do not own this feedback.")
    else:

        db.session.delete(to_be_deleted)
        db.session.commit()

        return redirect(f'/users/{username}')