from flask import Flask,render_template, flash, redirect, url_for, session, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, ValidationError, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

#configuration of my sql

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='Ge0f3!94'
app.config['MYSQL_DB']='myflaskapp'
app.config['MYSQL_CURSORCLASS']='DictCursor'

#init my sql
mysql=MySQL(app)

Articles = Articles()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def article():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:id>/')
def articles(id):
    return render_template('article.html', id=id)


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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

#logout
@app.route('/logout')
def logout():
    session.clear()
    flash("Your now logged out",'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
