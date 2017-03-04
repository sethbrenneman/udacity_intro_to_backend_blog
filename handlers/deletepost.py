from handler import Handler
from models.post import Post
from google.appengine.ext import db


class DeletePost(Handler):

    def get(self, post_id):
        # Checking user permissions
        post = Post.get_by_id(int(post_id))
        if not post:
            self.redirect('/')
        elif post.username != self.get_username():
            self.redirect('/login')
        # Delete the post from the database if everything checks out
        else:
            db.delete(post)
            self.redirect('/')
