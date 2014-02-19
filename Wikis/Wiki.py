# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="mcherry"
__date__ ="$Feb 4, 2014 3:19:28 PM$"

import cgi
import re
import random
import string
import time
import hashlib
import webapp2
import logging
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext import db
from BaseRenderingModule.BaseHandler import BaseHandler
        
lastCachedTime = time.time()

class WikiEntry(db.Model):
    page = db.StringProperty(required=True)
    content = db.StringProperty(required=True)
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now = True)
    created_by = db.StringProperty(required=True)
    last_modified_by = db.StringProperty(required=True)
    
class Wiki(BaseHandler):
    def get(self, entry_title=None):
        user= self.get_user()
        if entry_title == None:
            entry_title = "/FrontPage"
        entry = get_wiki_entry(entry_title)
        if not entry == None:
            self.render('WikiFrontPage.html', user = user, post = entry)
        elif not user == None:
            logging.error("the Entry is empty")
            self.redirect('/_edit%s' % entry_title)
        else:
            self.render('WikiFrontPage.html', user = user)
            

class WikiEdit(BaseHandler):
    
    def get(self, entry_title=None):
        self.write("Editing supposedly, lets get this on")
        entry = get_wiki_entry(entry_title)
        user_id = self.get_user()
        if user_id == None:
            self.redirect('')
        self.render('WikiEditPage.html', user = user_id, post = entry)
    
    def post(self, entry_title):
        user= self.get_user()
        logging.error("Entry on Post is %s" % entry_title)
        content = self.request.get("content")
        entry = get_wiki_entry(entry_title)
        if entry == None:
            entry = WikiEntry(page=entry_title, content=content, created_by=user, last_modified_by=user )
            entry.put()
            memcache.add(entry_title, entry)
        else:    
            entry.content = content
            entry.put()
        time.sleep(.4)
        self.redirect('%s' % entry_title)
            

def get_wiki_entry(entry_title):
    global lastCachedTime
    if entry_title == None:
        entry_title = "FrontPage"
    entry = memcache.get(entry_title)
    if not entry == None:
        entries = db.GqlQuery("Select * FROM WikiEntry WHERE page = :1", entry_title)
        if entries.count() > 0:
            entry = entries[0]
            lastCachedTime = time.time()
            memcache.add(entry_title, entry)
            return entry
    else:
        return entry