from handler import Handler
from models.post import Post
from models.comment import Comment
from google.appengine.ext import db


class ViewPost(Handler):

    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            self.redirect('/')
        else:
            self.render('post.html', post=post, comments=post.comments)

    def post(self, post_id):
        username = self.get_username()
        post = Post.get_by_id(int(post_id))

        # If the user is the owner of the post, the post method from the form
        # will be to edit the post
        if username == post.username:
            subject = self.request.get('subject')
            content = self.request.get('content')

            ok_form = True

            if not subject:
                error = 'You must enter a subject'
                ok_form = False
            if not ok_form and not content:
                self.redirect('/%s' % post_id)
            if ok_form and not content:
                error = 'You must enter some content'
                ok_form = False

            if ok_form:
                post.subject = subject
                post.content = self.br_substitution(content)
                post.put()
                self.redirect('/')

            else:
                post.subject = '%s ' % subject
                post.content = '%s ' % self.br_substitution(content)

                self.render("post.html", post=post, error=error)

        # If the user is not the owner of the post, redirect them to /login
        else:
            self.redirect('/login')
