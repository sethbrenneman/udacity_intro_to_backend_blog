from handler import Handler
from google.appengine.ext import db

class FrontPage(Handler):
  def get(self):
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")
    self.render("home.html", posts=posts)