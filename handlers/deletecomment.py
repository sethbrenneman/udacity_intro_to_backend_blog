from handler import Handler
from models.comment import Comment
from google.appengine.ext import db

class DeleteComment(Handler):
  def get(self, post_id, comment_id):
    # Check user permissions
    comment = Comment.get_by_id(int(comment_id))
    if not comment:
      self.redirect('/%s' % post_id)
    elif comment.username != self.get_username():
      self.redirect('/login')
    # Delete the comment if everything checks out
    else:
      db.delete(comment)
      self.redirect('/%s' % post_id)