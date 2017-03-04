from google.appengine.ext import db
from post import Post

class Like(db.Model):
  username = db.StringProperty(required=True)
  post = db.ReferenceProperty(Post, collection_name='likes', required=True)
  # post_id = db.IntegerProperty(required=True)