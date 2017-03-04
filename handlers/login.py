from handler import Handler
from google.appengine.ext import db
from hashing import check_password


class Login(Handler):

    def get(self):
        self.render('login.html', username='', errors={})

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        ok_form = True
        errors = {'username': '',
                  'password': ''}
        user = db.GqlQuery("SELECT * FROM User WHERE username='%s'"
                           % username).get()

        if not username:
            errors['username'] = 'You must enter a username'
            ok_form = False
        if ok_form and not user:
            errors['username'] = 'No such user is registered'
            ok_form = False
        if ok_form and not check_password(password, user.password):
            errors['password'] = 'Incorrect password'
            ok_form = False

        if not ok_form:
            self.render('login.html', username=username, errors=errors)

        else:
            self.set_cookie(username)
            self.redirect('/')
