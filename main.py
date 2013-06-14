"""A guestbook sample with sqlite3."""

import logging
import os

import jinja2
import sqlite3
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import modules
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

def get_connection():
    """A function to get sqlite connection.

    Returns:
        An sqlite connection object.
    """
    db_filename = os.path.join('/tmp', 'guestbook.sqlite')
    logging.info('Opened a sqlite db at {}.'.format(db_filename))
    return sqlite3.connect(db_filename)

def get_url_for_instance(instance_id):
    """Return a full url of the guestbook running on a particular instance.

    Args:
        A string to represent an VM instance.

    Returns:
        URL string for the guestbook form on the instance.
    """
    hostname = app_identity.get_default_version_hostname()
    return 'https://{}-dot-{}-dot-{}/guestbook'.format(
        instance_id, modules.get_current_version_name(), hostname)

def get_signin_navigation(original_url):
    """Return a pair of a link text and a link for sign in/out operation.
    
    Args:
        An original URL.

    Returns:
        Two values; a url and a link text.
    """
    if users.get_current_user():
        url = users.create_logout_url(original_url)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(original_url)
        url_linktext = 'Login'
    return url, url_linktext


class ActiveServer(ndb.Model):
    """A model to store active servers.

    We use the instance id as the key name.
    """
    instance_id = ndb.StringProperty(indexed=False)

class ListServers(webapp2.RequestHandler):
    """A handler for listing active servers."""
    def get(self):
        """A get handler for listing active servers."""
        key = ndb.Key(ActiveServer, 'Root')
        query = ActiveServer.query(ancestor=key)
        servers = []
        for key in query.iter(keys_only=True):
            instance_id = key.string_id()
            servers.append((instance_id, get_url_for_instance(instance_id)))
        template = JINJA_ENVIRONMENT.get_template('index.html')
        url, url_linktext = get_signin_navigation(self.request.uri)
        self.response.out.write(template.render(servers=servers,
                                                url=url,
                                                url_linktext=url_linktext))

class MainPage(webapp2.RequestHandler):
    """A handler for showing the guestbook form."""
    def get(self):
        """Guestbook main page."""
        con = get_connection()
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute('select * from guestbook order by id desc limit 20')
        greetings = cur.fetchall()
        con.close()
        template = JINJA_ENVIRONMENT.get_template('guestbook.html')
        url, url_linktext = get_signin_navigation(self.request.uri)
        self.response.out.write(template.render(greetings=greetings,
                                                url=url,
                                                url_linktext=url_linktext))

class Guestbook(webapp2.RequestHandler):
    """A handler for storing a message."""
    def post(self):
        """A handler for storing a message."""
        author = ''
        if users.get_current_user():
            author = users.get_current_user().nickname()
        con = get_connection()
        with con:
            con.execute('INSERT INTO guestbook (name, content) VALUES '
                        '(?, ?)', (author, self.request.get('content')))
        self.redirect('/guestbook')

class Start(webapp2.RequestHandler):
    """A handler for /_ah/start."""
    def get(self):
        """A handler for /_ah/start, registering myself."""
        con = get_connection()
        with con:
            con.execute('CREATE TABLE IF NOT EXISTS guestbook'
                        '(id integer PRIMARY KEY AUTOINCREMENT, name varchar, '
                        'content varchar)')
        instance_id = modules.get_current_instance_id()
        server = ActiveServer(key=ndb.Key(ActiveServer, 'Root',
                                          ActiveServer, instance_id))
        server.instance_id = instance_id
        server.put()

class Stop(webapp2.RequestHandler):
    """A handler for /_ah/stop."""
    def get(self):
        """A handler for /_ah/stop, de-registering myself."""
        instance_id = modules.get_current_instance_id()
        ndb.delete_multi([ndb.Key(ActiveServer, 'Root',
                                  ActiveServer, instance_id)])

APPLICATION = webapp2.WSGIApplication([
    ('/', ListServers),
    ('/guestbook', MainPage),
    ('/sign', Guestbook),
    ('/_ah/start', Start),
    ('/_ah/stop', Stop),
], debug=True)
