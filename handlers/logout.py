from handler import Handler


class Logout(Handler):

    def get(self):
        self.set_cookie()
        self.redirect('/')
