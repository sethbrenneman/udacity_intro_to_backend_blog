from handler import Handler
from models.post import Post
from models.like import Like
from google.appengine.ext import db

class VoteHandler(Handler):
  def get(self, post_id):
    post = Post.get_by_id(int(post_id))
    # Checking user permissions
    if not self.get_username():
      self.redirect('/login')
    elif post.username == self.get_username():
      self.redirect('/')
    # If the post is already liked by current user, 'unlike' aka delete the
    # like.  If the post is not already liked, create and put a new Like
    # in the database
    else:
      like = post.likes.filter('username', self.get_username()).get()
      if like:
        db.delete(like)
      else:
        l = Like(username=self.get_username(), post=post)
        l.put()
      self.redirect('/')