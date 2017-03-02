import os
import jinja2
import webapp2
import hashlib
import hmac
import re
import random
import string

from google.appengine.ext import db

logged_in = False

# IMPORTANT!  If deploying this app to Google's appspot
#             you must change the url string to your url
url = 'http://localhost:8080'

# Setting up jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               extensions=['jinja2.ext.do'],
                               autoescape=True)


def render_str(template, **params):
  t = jinja_env.get_template(template)
  return t.render(**params)

# Regular expressions for validating input
VALID_USERNAME = re.compile(r'^[a-zA-Z0-9_-]{3,20}$')
VALID_PASSWORD = re.compile(r'^[^|]{3,20}$')
VALID_EMAIL = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


# In user's posts, substitutes <br> in for newline characters so the
# html can render properly
def br_substitution(content):
  return content.replace('\n', '<br>')

# Hashing functions: for making and validating hashes

SECRET = 'uFxTzRVmbRmagKN9KYmu'


def hash_val(s):
  return hmac.new(SECRET, s).hexdigest()


def make_secure_val(s):
  return '%s|%s' % (s, hash_val(s))


def valid_user(h):
  user = h.split('|')[0]
  if make_secure_val(user) == h:
    return user


def make_salt(length=5):
  return ''.join(random.choice(string.letters) for l in range(length))


def make_hashed_password(p, salt=''):
  if not salt:
    salt = make_salt()
  return '%s|%s' % (salt, hashlib.sha256(salt + p).hexdigest())


def check_password(plaintext_password, hashed_password):
  salt = hashed_password.split('|')[0]
  if make_hashed_password(plaintext_password, salt=salt) == hashed_password:
    return True


# Setting up the database classes

class User(db.Model):
  username = db.StringProperty(required=True)
  password = db.StringProperty(required=True)
  email = db.StringProperty()


class Post(db.Model):
  subject = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  username = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  last_modified = db.DateTimeProperty(auto_now=True)


class Comment(db.Model):
  username = db.StringProperty(required=True)
  post_id = db.IntegerProperty(required=True)
  comment = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  last_modified = db.DateTimeProperty(auto_now=True)


class Like(db.Model):
  username = db.StringProperty(required=True)
  post_id = db.IntegerProperty(required=True)

# Some basic functions all handlers will need


class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **params):
    return render_str(template, **params)

# Each call of render always passes 3 keyword arguments to jinja2:
# url (str), logged_in(boolean), and username (str)
  def render(self, template, **params):
    params['url'] = url
    params['logged_in'] = self.login_status()
    username = self.get_username()
    if username:
      params['username'] = username
    else:
      params['username'] = ''
    self.write(self.render_str(template, **params))

  def login_status(self):
    global logged_in
    h = self.request.cookies.get('username')
    if not h:
      logged_in = False
    elif not valid_user(h):
        logged_in = False
    else:
      logged_in = True
    return logged_in

  def set_cookie(self, username=''):
    self.response.headers.add_header('Set-Cookie',
                                     str('username=%s; Path=/'
                                         % make_secure_val(username)))

  def get_username(self):
    username = self.request.cookies.get('username')
    if username:
      return username.split('|')[0]

# Specific Handlers


class FrontPage(Handler):
  def get(self):
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
    likes = db.GqlQuery("SELECT * FROM Like WHERE"
                        " username='%s'" % self.get_username())
    self.render("home.html", posts=posts, likes=likes)


class NewPost(Handler):
  def get(self):
    if not self.login_status():
      self.redirect('/login')
    else:
      self.render("new_post.html", subject='', content='', error='')

  def post(self):
    subject = self.request.get('subject')
    content = self.request.get('content')

    ok_form = True

    if not subject:
      error = 'You must enter a subject'
      ok_form = False
    if not ok_form and not content:
      self.redirect('/newpost')
    if ok_form and not content:
      error = 'You must enter some content'
      ok_form = False

    if ok_form:
      p = Post(subject=subject, content=br_substitution(content),
               username=valid_user(self.request.cookies.get('username')))
      p.put()
      self.redirect('/')

    else:
      self.render("new_post.html", subject=subject, content=content,
                  error=error)


class Signup(Handler):
  def get(self):
    self.render("signup.html", username="", email="", errors={})

  def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    verify = self.request.get("verify")
    email = self.request.get("email")
    query = db.GqlQuery("SELECT * FROM User WHERE username='%s'" % username)

    errors = {'username': '',
              'password': '',
              'verify': '',
              'email': ''}
    ok_form = True

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

    if ok_form:
      u = User(username=username, password=make_hashed_password(password),
               email=email)
      u.put()
      self.set_cookie(username)
      self.redirect('/welcome')
    else:
      self.render("signup.html", form_username=username, email=email,
                  errors=errors)


class Welcome(Handler):
  def get(self):
    username = valid_user(self.request.cookies.get('username'))
    if username:
      self.render('welcome.html', username=username)
    else:
      self.set_cookie()
      self.redirect('/')


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


class Logout(Handler):
  def get(self):
    self.set_cookie()
    self.redirect('/')


class ViewPost(Handler):

  def get(self, post_id):
    post = Post.get_by_id(int(post_id))
    if not post:
      self.redirect('/')
    else:
      comments = db.GqlQuery(("SELECT * FROM Comment WHERE post_id=%d"
                              "ORDER BY created ASC" % int(post_id)))
      self.render('post.html', post=post, comments=comments)

  def post(self, post_id):
    username = self.get_username()
    post = Post.get_by_id(int(post_id))
    comments = db.GqlQuery(("SELECT * FROM Comment WHERE post_id=%d"
                            "ORDER BY created ASC" % int(post_id)))

    if username == post.username:
      subject = self.request.get('subject')
      content = self.request.get('content')

      ok_form = True

      if not subject:
        error = 'You must enter a subject'
        ok_form = False
      if not ok_form and not content:
        self.redirect('/%s' % post_id)
      if ok_form and not content:
        error = 'You must enter some content'
        ok_form = False

      if ok_form:
        post.subject = subject
        post.content = br_substitution(content)
        post.put()
        self.redirect('/')

      else:
        post.subject = '%s ' % subject
        post.content = '%s ' % br_substitution(content)

        self.render("post.html", post=post, comments=comments,
                    error=error)

    elif not username:
      error = 'You must be logged in to comment'
      self.render("post.html", post=post, comments=comments, error=error)

    else:
      comment = self.request.get('comment')
      if not comment:
        error = 'You must enter a comment'
        post = Post.get_by_id(int(post_id))
        comments = db.GqlQuery(("SELECT * FROM Comment WHERE post='%s'"
                                "ORDER BY created ASC" % post_id))
        self.render('post.html', post=post, comments=comments,
                    error=error)
      else:
        c = Comment(username=self.get_username(), post_id=int(post_id),
                    comment=comment)
        c.put()
        self.redirect('/%s' % post_id)


class EditComment(Handler):
  def get(self, post_id, comment_id):
    c = Comment.get_by_id(int(comment_id))
    self.render('edit_comment.html', comment=c, error='')

  def post(self, post_id, comment_id):
    comment = self.request.get('comment')
    c = Comment.get_by_id(int(comment_id))
    if not comment:
      self.render('edit_comment.html', comment=c,
                  error='You must enter a comment')
    else:
      c.comment = comment
      c.put()
      self.redirect('/%s' % post_id)


class VoteHandler(Handler):
  def get(self, post_id):
    likes = db.GqlQuery("SELECT * FROM Like")
    post = Post.get_by_id(int(post_id))
    if not self.get_username():
      self.redirect('/login')
    elif post.username == self.get_username():
      self.redirect('/')
    else:
      like = db.GqlQuery("SELECT * FROM Like WHERE username='%s'"
                         " AND post_id=%d"
                         % (self.get_username(), int(post_id))).get()
      if like:
        db.delete(like)
      else:
        l = Like(username=self.get_username(), post_id=int(post_id))
        l.put()
      self.redirect('/')


class DeletePost(Handler):
  def get(self, post_id):
    post = Post.get_by_id(int(post_id))
    if not post:
      self.redirect('/')
    if post.username != self.get_username():
      self.redirect('/login')
    else:
      db.delete(post)
      self.redirect('/')


class DeleteComment(Handler):
  def get(self, post_id, comment_id):
    comment = Comment.get_by_id(int(comment_id))
    if not comment:
      self.redirect('/%s' % post_id)
    if comment.username != self.get_username():
      self.redirect('/login')
    else:
      db.delete(comment)
      self.redirect('/%s' % post_id)


app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/newpost', NewPost),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/([0-9]+)', ViewPost),
                               ('/([0-9]+)/([0-9]+)', EditComment),
                               ('/vote/([0-9]+)', VoteHandler),
                               ('/delete/([0-9]+)', DeletePost),
                               ('/delete/([0-9]+)/([0-9]+)', DeleteComment)],
                              debug=True)
