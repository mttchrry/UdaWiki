# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

from google.appengine.api import users
from google.appengine.ext import db
import hashlib
from BaseRenderingModule.BaseHandler import BaseHandler
import re
import cgi
import random
import string

def escape_html(s):
    return cgi.escape(s, quote=True)

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def create_cookie_hash(username, password, salt=""):
    if len(salt) == 0:
        salt = make_salt()
    h = hashlib.sha256(username + password + salt).hexdigest()
    return '%s_%s' % (h, salt)
    
def valid_pw(name, pw, h):
    key,salt = h.split('_')
    return h == create_cookie_hash(name, pw, salt)

class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)  
    email = db.StringProperty(required = False)

class SignUpPage(BaseHandler):
    def get(self):
        self.render('SignUpHtml.html', **{"userName":"","nameError":"","passwordError":"",
                                 "verifyError":"","email":"","emailError":""})

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')
        user_verify = self.request.get('verify')
        user_email = self.request.get('email')

        usernameerror = ''
        passworderror = ''
        verifyerror = ''
        emailerror = ''

        valid_form = True

        if not valid_username(user_username):
            usernameerror = "That's not a valid username."
            valid_form = False
        else: 
            user=db.GqlQuery("Select * FROM User WHERE username = '%s'" % user_username)
            if user.count() > 0:
                usernameerror = "User Already Exists."
                valid_form = False
        if not valid_password(user_password):
            passworderror = "That is not a valid password."
            valid_form = False
        elif user_password != user_verify:
            verifyerror = "Passwords don't match"
            valid_form = False
        if len(user_email) > 0 and not valid_email(user_email):
            emailerror = "Invalid email"
            valid_form = False

        username = escape_html(user_username)
        if valid_form == False:
            email = escape_html(user_email)
            self.render('SignUpHtml.html', **{"userName":username,"nameError":usernameerror,"passwordError":passworderror,
                                     "verifyError":verifyerror,"email":email,"emailError":emailerror})
        else:
            user=User(username=username, password=user_password, email=user_email)
            user.put()
            hash = create_cookie_hash(username, user_password)
            self.response.headers.add_header('Set-Cookie', "user_id=%s|%s; Path=/"%(str(user.key().id()), hash))
            self.redirect("/blog/welcome")

class Login(BaseHandler):
    def get(self):
        self.render('Login.html', **{"userName":"","invalid":""})

    def post(self):
        user_username = self.request.get('username')
        user_password = self.request.get('password')

        valid_form = True
        invalid_msg = "Invalid username and password"
        
        if not valid_username(user_username):
            valid_form = False
        else: 
            user=db.GqlQuery("Select * FROM User WHERE username = '%s'" % user_username)
            if user.count() == 0:
                valid_form = False
            else:
                if not user[0].password == user_password:
                    valid_form=False
                    
        if valid_form:
            hash = create_cookie_hash(user_username, user_password)
            self.response.headers.add_header('Set-Cookie', "user_id=%s|%s; Path=/"%(str(user[0].key().id()), hash))
            self.redirect('/blog/welcome')
        else:
            username = escape_html(user_username)
            self.render('Login.html', **{"userName":username,"invalid":invalid_msg})
            
class Logout(BaseHandler):
     def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/')
        #self.response.out.write("YouSignedOut")
        
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")

def valid_username(username):
    return USER_RE.match(username)

PASSWORD_RE = re.compile(r"^.{3,20}$")

def valid_password(password):
    return PASSWORD_RE.match(password)    

EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

def valid_email(email):
    return EMAIL_RE.match(email)
