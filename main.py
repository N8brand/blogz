from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:lc101@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#Define and initialize Blog db class
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title='', body=''):
        self.title = title
        self.body = body

# root path redirects to '/blog'
@app.route('/')
def index():
    return redirect('/blog')

# /blog path 
@app.route('/blog')
def blog():
    # Queries Blog db to order all by descending id (newest to oldest)
    blogs = Blog.query.order_by(Blog.id.desc()).all()   
    # if querying for specific post
    if request.args:
        # get id from db
        id=request.args.get('id')
        # set variabales equal to individual query data
        title = Blog.query.filter_by(id=id).first().title
        body = Blog.query.filter_by(id=id).first().body
        # display contents of single post
        return render_template('singlepost.html',title=title,body=body)
    else:
        # display main blog page listing all entries
        return render_template('blog.html', blogs=blogs)

# /newpost path
@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    # display newpost.html form
    if request.method=='GET':
        return render_template('newpost.html')
    # submit new form
    if request.method=='POST':
        title=request.form['title']
        body=request.form['body']
        blog_error=''
    # if title or body remain empty, raise error
    if title=='' or body=='':
        blog_error='Your post must contain both a Title and a Body'
    # if no blog error raised, commit new blog data to db, and show individual blog addition
    if blog_error=='':
        new_blog=Blog(title,body)
        db.session.add(new_blog)
        db.session.commit()
        # set variable equal to /blog query route for specific entry
        query_url= './blog?id='+ str(new_blog.id)
        # redirect to /blog displaying singlepost.html for new_blog entry
        return redirect(query_url)
    else:
        # remain on newpost.html, display blog_error, retain title and body text data entered
        return render_template('newpost.html', error=blog_error, title=title, body=body)

if __name__=='__main__':
    app.run()