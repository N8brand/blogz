from flask import request, render_template, flash, session, redirect
from sqlalchemy import desc
from app import app, db
from models import User, Blog

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'view_blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Welcome, ' +username, 'not_error')
            return redirect('/blog?user=' + str(user.username))
        else:
            flash('Password is incorrect, or user does not exist', 'error')
            return render_template('login.html', username=username)
    
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if password != verify:
            flash('Passwords do not match', 'error')
            return render_template('signup.html', username=username)
        if len(username) < 4:
            flash('Username must be longer than 3 characters', 'error')
            return render_template('signup.html')
        if len(password) < 4:
            flash('Password must be longer than 3 characters', 'error')
            return render_template('signup.html', username=username)
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog?user=' +str(new_user.username))
        else:
            flash('User already exists', 'error')
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        if title != "" and body != "":
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            id = str(new_post.id)
            return redirect('/blog?id='+id)
        else:
            flash("Please make sure neither field is empty!", 'error')
            return render_template('newpost.html', title=title, body=body)

    return render_template('newpost.html')

@app.route('/blog', methods=['GET'])
def view_blog():
    id = request.args.get('id')
    username = request.args.get('user')

    
    if id:
        blog_post = Blog.query.filter_by(id=id).first()
        title = blog_post.title
        body = blog_post.body
        owner_id = blog_post.owner_id
        owner = User.query.filter_by(id=owner_id).first()
        return render_template('blog.html', title=title, body=body, owner=owner)
    
    if username: 
        user = User.query.filter_by(username=username).first()
        user_blogs = Blog.query.filter_by(owner_id=user.id).order_by(desc(Blog.id)).all()
        return render_template('user.html', user=user, user_blogs=user_blogs)

    posts = Blog.query.order_by(desc(Blog.id)).all()

    return render_template('bloglist.html', posts=posts)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()