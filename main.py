from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

app.secret_key = 'jakebright' 


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'home']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/home')
def home():
    users = User.query.filter_by().all()
    
    return render_template('blog_index.html', users=users)


@app.route('/login', methods=['POST', 'GET'])
def login ():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')


    return render_template('login.html')

@app.route('/signup', methods=['POST' , 'GET'])
def signup():    

    has_errors = False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        
        username_error= ''
        password_error = ''
        verify_error = ''
        email_error = ''

        # username verifacatction
        if len(username) > 20 or len(username) < 3:
            username_error= '3-20 characters please'
            username= ''
            
            has_errors= True

        if ' ' in username:
            username_error= 'Cannot contain spaces'
            username= ''

            has_errors= True
        
        #password verifacation
        if len(password) > 20 or len(password) < 3:
            password_error= '3-20 characters please'
            password= ''

            has_errors= True
            
        if len(verify) == 0:
            verify_error= 'Cannot leave blank'
            verify= ''

            has_errors= True
        
        if password != verify:
            verify_error= 'Passwords must match'
            verifypassword= ''
        
            has_errors = True

        if ' ' in password:
            password_error= 'Cannot contain spaces'
            password= ''

            has_errors= True

        if has_errors == True:

            return render_template('signup.html', username_error= username_error, 
                password_error= password_error, verify_error= verify_error, password=password,
                username=username, form= request.form)

        #TODO-Validate

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username


            return redirect('/newpost')

        else:
            #TODO- message
            return '<h1> duplicate user </h1>'

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/login')

@app.route('/post/<int:post_id>/')
def post(post_id):
    post = Blog.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)

@app.route('/blog', methods=['POST', 'GET'])
def display_all_posts():
    #import pdb; pdb.set_trace()
    has_errors = False
    owner = User.query.filter_by(username=session['username']).first()
    users = User.query.filter_by().all()

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
                body_error=body_error, form=request.form, title=title, body=body)      #, form=request.form

        blog_title = request.form['title']
        blog_body =  request.form['body']
        new_blog = Blog(title, body, owner)
        db.session.add(new_blog)
        db.session.commit()

        return redirect('/post/%s/' % new_blog.id )


    if request.method == 'GET':
        user = request.args.get('id', None)
        _user = User.query.filter_by(username=user).first()

        if _user is None:
            blogs = Blog.query.filter_by().all()
            
                #import pdb; pdb.set_trace()
        else:
            blogs = Blog.query.filter_by(owner_id=_user.id).all()
        for blog in blogs:
            _user = User.query.filter_by(id=blog.owner_id).first()
            setattr(blog,'user', _user)

            
        
        return render_template('blog.html', title='Blogz', blogs=blogs)

@app.route('/my_blogs')
def my_blogs():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'GET':
        blogs = Blog.query.filter_by(owner=owner).all()
        
        return render_template('my_blogs.html', title='My Blogz', blogs=blogs)
  


@app.route('/newpost', methods=['POST' , 'GET'])
def add_post():  
    
    return render_template('newpost.html')

@app.route('/', methods =['POST' , 'GET'])
def index():
    return redirect('/blog')
    #return render_template('singlepage.html')

if __name__ == '__main__':
    app.run()
