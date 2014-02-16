# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.
import webapp2

from BaseRenderingModule.BaseHandler import BaseHandler
from Login.Login import SignUpPage
from Login.Login import Login
from Login.Login import Logout
from Wikis.Wiki import Wiki
from Wikis.Wiki import WikiEdit

PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
app = webapp2.WSGIApplication([
    ('/', Wiki),
    ('/signup', SignUpPage),
    ('/login', Login),
    ('/logout', Logout),
    ('/_edit' + PAGE_RE, WikiEdit),
    (PAGE_RE, Wiki)
], debug=True)
