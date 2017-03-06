from handler import Handler
from models.comment import Comment
from models.post import Post
from google.appengine.ext import db


class CommentHandler(Handler):

    def get(self, post_id):
        self.post(post_id)

    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            self.redirect('/')
        elif not self.login_status():
            self.redirect('/%s' % post_id)
        else:
            comment = self.request.get('comment')
            if not comment:
                error = 'You must enter a comment'
                self.render('post.html', post=post, error=error)
            else:
                c = Comment(username=self.get_username(), post=post,
                            comment=self.br_substitution(comment))
                c.put()
                self.redirect('/%s' % post_id)
