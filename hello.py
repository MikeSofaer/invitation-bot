import sys
sys.path.append('./google_appengine')
sys.path.append('./google_appengine/lib')
sys.path.append('./google_appengine/lib/webob') 

from waveapi import events
from waveapi import model
from waveapi import robot

import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Participant(db.Model):
  email_to_add = db.StringProperty(multiline=False)
  added = db.BooleanProperty(default = False)
  date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.out.write('<html><body>')

    participants = db.GqlQuery("SELECT * FROM Participant ORDER BY date DESC LIMIT 10")

    for participant in participants:
      value = participant.email_to_add
      if value != None:
        self.response.out.write('<b>%s</b> asked to join:' % cgi.escape(value))
        self.response.out.write('  Joined field is: <b>%s</b></br>' % participant.added)
 
    # Write the submission form and the footer of the page
    self.response.out.write("""
          <form action="/sign" method="post">
            <div><textarea name="email" rows="3" cols="60"></textarea></div>
            <div><input type="submit" value="Enter sandbox email"></div>
          </form>
          <br/>Users are added any time the wave is updated (I haven't figured out CRON yet) and everyone is re-added (I need to figure out how to set the "added" flag to true).<br/>You can add this robot to a wave to invite everyone who has joined on this web form to that wave.<br/>The source for this wave is available <a href = "http://github.com/MikeSofaer/invitation-bot/tree/master">on my github</a>.
        </body>
      </html>""")

class WaveList(webapp.RequestHandler):
  def post(self):
    participant = Participant()

    participant.email_to_add = self.request.get('email')
    participant.put()
    self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', WaveList)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()