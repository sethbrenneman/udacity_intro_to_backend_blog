from handler import Handler
from hashing import valid_user

class Welcome(Handler):
  def get(self):
    username = valid_user(self.request.cookies.get('username'))
    if username:
      self.render('welcome.html', username=username)
    else:
      self.set_cookie()
      self.redirect('/')