from flask import Flask,render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, ValidationError, validators
from passlib.hash import sha256_crypt
from functools import wraps

def create_app():
  app = Flask(__name__)
  return app
#configuration of my sql
app = create_app()
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Ge0f3!94'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#init my sql
mysql=MySQL(app)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/article/<string:id>/')
def article(id):
    # creating cursor
    cur = mysql.connection.cursor()

    # fecting articles

    result = cur.execute("SELECT * FROM articles where id=%s",[id])

    article = cur.fetchone()

    return render_template('article.html', article=article)


@app.route('/articles')
def articles():
    # creating cursor
    cur = mysql.connection.cursor()

    # fecting articles

    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = "NO Articles found"
        return render_template('articles.html', articles=articles)

    # closing connection
    cur.close()


class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=10, max=100)])
    username = StringField('UserName', [validators.length(min=1, max=100)])
    email = StringField('Email', [validators.length(min=1, max=100)])
    password = PasswordField("password", [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password doesn't match")]
                             )
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        name=form.name.data
        email=form.email.data
        username=form.username.data
        password=sha256_crypt.encrypt(form.password.data)
        #creating cursor
        cur = mysql.connection.cursor()
        cur.execute("Insert into users(name,email,username,password) VALUES (%s,%s,%s,%s)",(name,email,username,password))
        # commit to DD
        mysql.connection.commit()
        #closing the connection
        cur.close()

        flash("Your now Registered ! Go ahed and login with your credentials","success")
        redirect(url_for('index'))
        return render_template('register.html',form=form)

    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username']
        password_user =request.form['password']

        #creating cursor
        cur = mysql.connection.cursor()

        #get password for the particular user from the users table
        result = cur.execute('Select * from users where username=%s',[username])

        #if there is a user with that username
        if result >0:
            #get Stored Hash
            data = cur.fetchone()
            password = data['password']

            #compare userpassword with password
            if sha256_crypt.verify(password_user,password):
                session['logged in']=True
                session['username']=username

                flash("your are now logged in ",'success')
                return redirect(url_for('dashboard'))
            else:
                error="Invalid Login credentials"
                return render_template('login.html', error=error)
                app.logger.info("Password not Matched")
        else:
            error ='Username Not found'
            return render_template('login.html', error=error)
            app.logger.info("User Not Matched")
            #closing the cursor
            cur.close()

    return render_template('login.html')

#check if the user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in'):
            flash("authorized user ", 'success')
            return f(*args, **kwargs)
        else:
            flash("Unauthorized user please login", 'danger')
            return redirect(url_for("login"))

    return wrap


@app.route('/dashboard')
#@is_logged_in
def dashboard():

    #creating cursor
    cur = mysql.connection.cursor()

    #fecting articles

    result = cur.execute("SELECT * FROM articles")

    articles=cur.fetchall()

    if result>0:
        return render_template('dashboard.html',articles=articles)
    else:
        msg = "NO Articles found"
        return  render_template('dashboard.html',articles=articles)

    #closing connection
    cur.close()

    return render_template('dashboard.html')

#article form
class ArticleFrom(Form):
    title = StringField('Title', [validators.length(min=10, max=200)])
    body = TextAreaField('Body', [validators.length(min=30)])

#edit article
@app.route('/edit_article/<string:id>',methods=['POST','GET'])
#@is_logged_in
def edit_article(id):

    #create cursor
    cur = mysql.connection.cursor()
    #get article by id
    result=  cur.execute("select * from articles where id=%s",[id])

    article = cur.fetchone()

    form = ArticleFrom(request.form)

    #populate article form fields

    form.title.data =article['title']
    form.body.data =article['body']

    if request.method =='POST' and form.validate():

        title = request.form['title']
        body = request.form['body']


        # creating cursor
        cur=mysql.connection.cursor()

        #sql query
        cur.execute("UPDATE articles set title=%s ,body=%s where id=%s",(title,body,id))

        # commit to db
        mysql.connection.commit()

        cur.close()

        flash('Aritcle Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html',form=form)

#Delete_article
@app.route('/delete_article<string:id>',methods=['POST'])
def delete_article(id):
    #create cursor
    cur = mysql.connection.cursor()

    #executing delete statement
    cur.execute('delete from articles where id=%s',[id])

    #commit to db
    mysql.connection.commit()

    cur.close()

    flash('Article Deleted','success')

    return redirect(url_for('dashboard'))


#add article
@app.route('/add_article',methods=['POST','GET'])
#@is_logged_in
def add_article():
    form = ArticleFrom(request.form)

    if request.method =='POST' and form.validate():

        title = form.title.data
        body = form.body.data


        # creating cursor
        cur=mysql.connection.cursor()

        #sql query
        cur.execute("insert into articles(title,body,author) VALUES (%s,%s,%s)",(title,body,session['username']))

        # commit to db
        mysql.connection.commit()

        cur.close()

        flash("Article list updated ",'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html',form=form)

#logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Your now logged out",'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
