from handler import Handler
from models.comment import Comment


class EditComment(Handler):

    def get(self, post_id, comment_id):
        # Checking to make sure current user has permission
        c = Comment.get_by_id(int(comment_id))
        if not self.get_username():
            self.redirect('/%s' % post_id)
        elif not c or not (self.get_username() == c.username):
            self.redirect('/%s' % post_id)
        else:
            self.render('edit_comment.html', comment=c, error='')

    def post(self, post_id, comment_id):
        # Checking user permission
        c = Comment.get_by_id(int(comment_id))
        if not self.get_username():
            self.redirect('/%s' % post_id)
        elif not c:
            self.redirect('/%s' % post_id)
        elif not (self.get_username() == c.username):
            self.redirect('/login')
        else:
            comment = self.request.get('comment')
            if not comment:
                self.render('edit_comment.html', comment=c,
                            error='You must enter a comment')
            else:
                c.comment = self.br_substitution(comment)
                c.put()
                self.redirect('/%s' % post_id)
