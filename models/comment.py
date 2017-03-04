from google.appengine.ext import db
from post import Post

class Comment(db.Model):
  username = db.StringProperty(required=True)
  # post_id = db.IntegerProperty(required=True)
  post = db.ReferenceProperty(Post, collection_name = 'comments',
                              required=True)
  comment = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  last_modified = db.DateTimeProperty(auto_now=True)