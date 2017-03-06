import webapp2

from handlers.frontpage import FrontPage
from handlers.newpost import NewPost
from handlers.signup import Signup
from handlers.welcome import Welcome
from handlers.login import Login
from handlers.logout import Logout
from handlers.viewpost import ViewPost
from handlers.comment import CommentHandler
from handlers.editcomment import EditComment
from handlers.votehandler import VoteHandler
from handlers.deletepost import DeletePost
from handlers.deletecomment import DeleteComment


app = webapp2.WSGIApplication([('/', FrontPage),
                               ('/newpost', NewPost),
                               ('/signup', Signup),
                               ('/welcome', Welcome),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/([0-9]+)', ViewPost),
                               ('/comment/([0-9]+)', CommentHandler),
                               ('/([0-9]+)/([0-9]+)', EditComment),
                               ('/vote/([0-9]+)', VoteHandler),
                               ('/delete/([0-9]+)', DeletePost),
                               ('/delete/([0-9]+)/([0-9]+)', DeleteComment)],
                              debug=True)
