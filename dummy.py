"""Dummy robot only."""
 
__author__ = 'davidbyttow@google.com (David Byttow)'
 
from waveapi import events
from waveapi import model
from waveapi import robot
from google.appengine.ext import db 
import cgi

class Participant(db.Model):
  email_to_add = db.StringProperty(multiline=False)
  added = db.BooleanProperty(default = False)
  date = db.DateTimeProperty(auto_now_add=True)

def OnParticipantsChanged(properties, context):
  """Invoked when any participants have been added/removed."""
	  
def OnDocumentChanged(properties, context):
  """Invoked when document changes"""
  InviteAll(context)

def InviteAll(context):	  
  root_wavelet = context.GetRootWavelet()
  participants = db.GqlQuery("SELECT * FROM Participant ORDER BY date DESC")
  for participant in participants:
    value = participant.email_to_add
    if ((value != None) and (str(value).lower().endswith("@wavesandbox.com") or str(value).lower().endswith("gwave.com"))):
      output = root_wavelet.AddParticipant(cgi.escape(str(value).lower()))
      participant.added = True
      participant.put
	  
def Announce(context):
  """Called when this robot is first added to the wave."""
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("I'm alive!")
 
def OnUpdate(context):
  root_wavelet = context.GetRootWavelet()
  root_wavelet.CreateBlip().GetDocument().SetText("I'm a crontask!")
  
if __name__ == '__main__':
  dummy = robot.Robot('Invitation-bot',
                      image_url='http://invitation-bot.appspot.com/icon.png',
                      profile_url='http://invitation-bot.appspot.com/')
  dummy.RegisterHandler(events.WAVELET_PARTICIPANTS_CHANGED,
                        OnParticipantsChanged)
  dummy.RegisterHandler(events.DOCUMENT_CHANGED,
                        OnDocumentChanged)
  dummy.RegisterCronJob("/_wave/robot/update", 10)						
  dummy.Run()
