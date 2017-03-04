from handler import Handler
from hashing import valid_user
from models.post import Post


class NewPost(Handler):

    def get(self):
        if not self.login_status():
            self.redirect('/login')
        else:
            self.render("new_post.html", subject='', content='', error='')

    def post(self):
        if not self.login_status():
            self.redirect('/login')
        subject = self.request.get('subject')
        content = self.request.get('content')

        # Form Validation
        ok_form = True

        if not subject:
            error = 'You must enter a subject'
            ok_form = False
        if not ok_form and not content:
            self.redirect('/newpost')
        if ok_form and not content:
            error = 'You must enter some content'
            ok_form = False

        if ok_form:
            p = Post(subject=subject, content=self.br_substitution(content),
                     username=valid_user(self.request.cookies.get('username')))
            p.put()
            self.redirect('/')

        else:
            self.render("new_post.html", subject=subject, content=content,
                        error=error)
