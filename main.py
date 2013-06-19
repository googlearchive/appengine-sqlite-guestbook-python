"""A guestbook sample with sqlite3."""

import logging
import os

import jinja2
import sqlite3
import webapp2

from google.appengine.api import app_identity
from google.appengine.api import modules
from google.appengine.api import runtime
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

DB_FILENAME = os.path.join('/tmp', 'guestbook.sqlite')

CREATE_TABLE_SQL = """\
CREATE TABLE IF NOT EXISTS guestbook
(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR, content VARCHAR)"""

SELECT_SQL = 'SELECT * FROM guestbook ORDER BY id DESC LIMIT {}'

INSERT_SQL = 'INSERT INTO guestbook (name, content) VALUES (?, ?)'

POST_PER_PAGE = 20


def shutdown_hook():
    """A hook function for de-registering myself."""
    logging.info('shutdown_hook called.')
    instance_id = modules.get_current_instance_id()
    ndb.transaction(
        lambda: ActiveServer.get_instance_key(instance_id).delete())


def get_connection():
    """A function to get sqlite connection.

    Returns:
        An sqlite connection object.
    """
    logging.info('Opening a sqlite db.')
    return sqlite3.connect(DB_FILENAME)


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
        Two value tuple; a url and a link text.
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

    We use the instance id as the key name, and there are no properties.
    """

    @classmethod
    def get_instance_key(cls, instance_id):
        """Return a key for the given instance_id.

        Args:
            An instance id for the server.

        Returns:
            A Key object which has a common parent key with the name 'Root'.
        """
        return ndb.Key(cls, 'Root', cls, instance_id)


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
        cur.execute(SELECT_SQL.format(POST_PER_PAGE))
        greetings = cur.fetchall()
        con.close()
        template = JINJA_ENVIRONMENT.get_template('guestbook.html')
        url, url_linktext = get_signin_navigation(self.request.uri)
        self.response.write(template.render(greetings=greetings,
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
            con.execute(INSERT_SQL, (author, self.request.get('content')))
        self.redirect('/guestbook')


class Start(webapp2.RequestHandler):
    """A handler for /_ah/start."""

    def get(self):
        """A handler for /_ah/start, registering myself."""
        runtime.set_shutdown_hook(shutdown_hook)
        con = get_connection()
        with con:
            con.execute(CREATE_TABLE_SQL)
        instance_id = modules.get_current_instance_id()
        server = ActiveServer(key=ActiveServer.get_instance_key(instance_id))
        server.put()


class Stop(webapp2.RequestHandler):
    """A handler for /_ah/stop."""

    def get(self):
        """Just call shutdown_hook now for a temporary workaround.

        With the initial version of the vm runtime, a call to
        /_ah/stop hits this handler, without invoking the shutdown
        hook we registered in the start handler. We're working on the
        fix to make it a consistent behavior same as the traditional
        App Engine backends. After the fix is out, this stop handler
        won't necessary any more.
        """
        shutdown_hook()


APPLICATION = webapp2.WSGIApplication([
    ('/', ListServers),
    ('/guestbook', MainPage),
    ('/sign', Guestbook),
    ('/_ah/start', Start),
    ('/_ah/stop', Stop),
], debug=True)
