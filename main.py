from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y37kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, body, owner):
        self.name = name
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username=username
        self.password=password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_error =''
        password_error =''

        user = User.query.filter_by(username=username).first()
        if username =='':
            user_error = 'Please input a username'
            return render_template('login.html', user_error=user_error)
        else:
            if not user:
                user_error = 'This is not an existing username/invalid input'
            if not user.password == password or password=='':
                password_error = 'Invalid password/Please input a password'
            
            if not user_error and not password_error:
                session['username']  = username
                flash("Logged in")
                return redirect('/new-blog?username='+str(username))
            else:   
                return render_template ('login.html', user_error=user_error, password_error=password_error, username=username)
    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        username_error=''
        password_error=''
        verify_error=''

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if len(username) < 3 or len(username) > 20 or " " in username:
                username_error = "This is not a valid username"

            if len(password) < 3 or len(password) > 20 or " " in password:
                password_error = "This is not a valid password"
   
            if not verify == password:
                verify_error = "The verification of the password does NOT match"
    
            if not username_error and not password_error and not verify_error:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/new-blog?username='+str(username))
            else:
                return render_template('signup.html', username=username, username_error=username_error, password=password, password_error = password_error, verify=verify, verify_error=verify_error)
        else:
            return '<h1>Duplicate user</h1>'

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')


@app.route('/index', methods=['GET'])
def index():

    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/main-blog', methods=['POST', 'GET'])
def main_blog():

    user_id = str(request.args.get('user'))
    owner = Blog.query.filter_by(id=user_id).first()

    blog_id = str(request.args.get('id'))
    new_blog = Blog.query.get(blog_id)
    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('main-blog.html', new_blog=new_blog, blogs=blogs)

@app.route('/new-blog', methods=['POST', 'GET'])
def create_blog_post():

    if request.method == 'POST':
        post_title = request.form['post-title'] 
        body_post = request.form['body-post']  
        post_title_error = ""
        body_post_error = ""

        if len(post_title) <1:
            post_title_error = "Input Title"
        if len(body_post) <1:
            body_post_error = "Input Body of Post"
        
        if not post_title_error and not body_post_error:
            owner = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(post_title, body_post, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect ('/main-blog?id='+str(new_blog.id)) 
        else:
            return render_template('new-blog-post.html', post_title_error=post_title_error, body_post_error=body_post_error)          
    else:
        return render_template('new-blog-post.html')

if __name__ == '__main__':
    app.run()