import re

from models.user import User
from handler import Handler
from hashing import make_hashed_password
from google.appengine.ext import db

# Regular expressions for validating input
VALID_USERNAME = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
VALID_PASSWORD = re.compile(r'^[^|]{3,20}$')
VALID_EMAIL = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


class Signup(Handler):

    def get(self):
        self.render("signup.html", username="", email="", errors={})

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")
        query = db.GqlQuery(
            "SELECT * FROM User WHERE username='%s'" % username)

        # Create dictionary of errors to pass to the template.  The error messages
        # are initially empty, but will be changed to reflect errors on the
        # form.
        errors = {'username': '',
                  'password': '',
                  'verify': '',
                  'email': ''}
        ok_form = True

        # Form validation
        if not username:
            errors['username'] = 'You must enter a username'
            ok_form = False
        elif not VALID_USERNAME.match(username):
            errors['username'] = ('Username must consist of letters, digits, '
                                  '_ or -, and must be 3 - 20 characters')
            ok_form = False
        elif query.count() != 0:
            errors['username'] = 'Username is already taken'
            ok_form = False
        if not password:
            errors['password'] = 'You must enter a password'
            ok_form = False
        elif not VALID_PASSWORD.match(password):
            errors['password'] = ('Passwords must be 3 - 20 characters in length, '
                                  'and cannot include the "|" pipe character')
            ok_form = False
        if not verify:
            errors['verify'] = ('You must re-enter your password'
                                ' to confirm it is correct')
            ok_form = False
        elif password != verify:
            errors['verify'] = 'Your passwords do not match'
            ok_form = False
        if email:
            if not VALID_EMAIL.match(email):
                errors['email'] = 'Invalid email address'
                ok_form = False

        # Rendering the page
        if ok_form:
            u = User(username=username, password=make_hashed_password(password),
                     email=email)
            u.put()
            self.set_cookie(username)
            self.redirect('/welcome')
        else:
            self.render("signup.html", form_username=username, email=email,
                        errors=errors)
