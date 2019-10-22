from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, name, body):
        self.name = name
        self.body = body






@app.route('/main-blog', methods=['GET'])
def index():

    blog_id = str(request.args.get('id'))
    new_blog = Blog.query.get(blog_id)
    blogs = Blog.query.all()
    return render_template('main-blog.html', blogs=blogs, new_blog=new_blog)

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
            new_blog = Blog(post_title, body_post)
            db.session.add(new_blog)
            db.session.commit()
            return redirect ('/main-blog?id='+str(new_blog.id)) #, new_blog=new_blog)
        else:
            return render_template('new-blog-post.html', post_title_error=post_title_error, body_post_error=body_post_error) 
           
    else:
        return render_template('new-blog-post.html')

if __name__ == '__main__':
    app.run()