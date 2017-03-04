import webapp2
import os
import jinja2
from hashing import make_secure_val, valid_user

# Setting up the jinja environment
template_dir = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               extensions=['jinja2.ext.do'],
                               autoescape=True)

def render_str(template, **params):
  t = jinja_env.get_template(template)
  return t.render(**params)

class Handler(webapp2.RequestHandler):

  # IMPORTANT! By default, this app will only run on a local machine.
  # If you want to deploy it to Google's appspot, change url to the path
  # of your gcloud app
  # e.g.
  # url = 'http://seths-udacity-project.appspot.com'
  url = 'http://seths-udacity-project.appspot.com'

  # Some helper functions that will be common to all handlers

  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def br_substitution(self, content):
    return content.replace('\n', '<br>')

  def render_str(self, template, **params):
    return render_str(template, **params)

  # Each call of render always passes 3 keyword arguments to jinja2:
  # url (str), logged_in(boolean), and username (str)
  def render(self, template, **params):
    params['url'] = self.url
    params['logged_in'] = self.login_status()
    username = self.get_username()
    if username:
      params['username'] = username
    else:
      params['username'] = ''
    self.write(self.render_str(template, **params))

  def login_status(self):
    logged_in = False
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
      return valid_user(username)