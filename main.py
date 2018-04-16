from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'jakebright' 


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

# create route
#render template
#link to route and id
#return

@app.route('/post/<int:post_id>/')
def post(post_id):
    post = Blog.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

@app.route('/blog', methods=['POST', 'GET'])
def display_all_posts():
    #import pdb; pdb.set_trace()
    has_errors = False
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title_error = ''
        body_error = ''

        if len(title) == 0:
            title_error = 'There must be content'
            title = ''

            has_errors = True

        if len(body) == 0:
            body_error = 'There must be content'
            body = ''

            has_errors = True

        if has_errors == True:

            return render_template('newpost.html', title_error=title_error, 
                body_error=body_error)      #, form=request.form

        blog = Blog(request.form['title'], request.form['body'])
        db.session.add(blog)
        db.session.commit()

        return redirect('/post/%s/' % blog.id )

    if request.method == 'GET':
        blogs = Blog.query.all()
        
        return render_template('blog.html', title='build-a-blog', blogs=blogs)
  

@app.route('/newpost', methods=['GET'])
def add_post():  
    
    return render_template('newpost.html')

@app.route('/', methods =['POST' , 'GET'])
def index():
    return redirect('/blog')
    #return render_template('singlepage.html')

if __name__ == '__main__':
    app.run()

