from flask import Flask,render_template, flash, redirect, url_for, sessions, logging, request
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, ValidationError, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

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
    password = PasswordField('password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Password doesn't match")]
                             )
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method=='POST' and form.validate():
        return render_template('register.html',form=Form)
    else:
        return render_template('register.html',form=Form)

'''@app.route('/register')
def register():
    return  render_template('register.html')'''
if __name__ == '__main__':
    app.run(debug=True)
