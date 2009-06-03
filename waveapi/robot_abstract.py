#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines the generic robot classes.

This module provides the Robot class and RobotListener interface,
as well as some helper functions for web requests and responses.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'

import model
import ops
import simplejson
import util


def ParseJSONBody(json_body):
  """Parse a JSON string and return a context and an event list."""
  json = simplejson.loads(json_body)
  # TODO(davidbyttow): Remove this once no longer needed.
  data = util.CollapseJavaCollections(json)
  context = ops.CreateContext(data)
  events = [model.CreateEvent(event_data) for event_data in data['events']]
  return context, events


def SerializeContext(context):
  """Return a JSON string representing the given context."""
  context_dict = util.Serialize(context)
  return simplejson.dumps(context_dict)


class RobotListener(object):
  """Listener interface for robot events.

  The RobotListener is a high-level construct that hides away the details
  of events. Instead, a client will derive from this class and register
  it with the robot. All event handlers are automatically registered. When
  a relevant event comes in, logic is applied based on the incoming data and
  the appropriate function is invoked.

  For example:
    If the user implements the "OnRobotAdded" method, the OnParticipantChanged
    method of their subclass, this will automatically register the
    events.WAVELET_PARTICIPANTS_CHANGED handler and respond to any events
    that add the robot.

    class MyRobotListener(robot.RobotListener):

      def OnRobotAdded(self):
        wavelet = self.context.GetRootWavelet()
        blip = wavelet.CreateBlip()
        blip.GetDocument.SetText("Thanks for adding me!")

    robot = robots.Robot()
    robot.RegisterListener(MyRobotListener)
    robot.Run()

  TODO(davidbyttow): Implement this functionality.
  """

  def __init__(self):
    pass

  def OnRobotAdded(self):
    # TODO(davidbyttow): Implement.
    pass

  def OnRobotRemoved(self):
    # TODO(davidbyttow): Implement.
    pass


class Robot(object):
  """Robot metadata class.

  This class holds on to basic robot information like the name and profile.
  It also maintains the list of event handlers and cron jobs and
  dispatches events to the appropriate handlers.
  """

  def __init__(self, name, image_url='', profile_url=''):
    """Initializes self with robot information."""
    self._handlers = {}
    self.name = name
    self.image_url = image_url
    self.profile_url = profile_url
    self.cron_jobs = []

  def RegisterHandler(self, event_type, handler):
    """Registers a handler on a specific event type.

    Multiple handlers may be registered on a single event type and are
    guaranteed to be called in order.

    The handler takes two arguments, the event properties and the Context of
    this session. For example:

    def OnParticipantsChanged(properties, context):
      pass

    Args:
      event_type: An event type to listen for.
      handler: A function handler which takes two arguments, event properties
          and the Context of this session.
    """
    self._handlers.setdefault(event_type, []).append(handler)

  def RegisterCronJob(self, path, seconds):
    """Registers a cron job to surface in capabilities.xml."""
    self.cron_jobs.append((path, seconds))

  def HandleEvent(self, event, context):
    """Calls all of the handlers associated with an event."""
    for handler in self._handlers.get(event.type, []):
      # TODO(jacobly): pass the event in to the handlers directly
      # instead of passing the properties dictionary.
      handler(event.properties, context)

  def GetCapabilitiesXml(self):
    """Return this robot's capabilities as an XML string."""
    lines = ['<w:capabilities>']
    for capability in self._handlers:
      lines.append('  <w:capability name="%s"/>' % capability)
    lines.append('</w:capabilities>')

    if self.cron_jobs:
      lines.append('<w:crons>')
      for job in self.cron_jobs:
        lines.append('  <w:cron path="%s" timerinseconds="%s"/>' % job)
      lines.append('</w:crons>')

    robot_attrs = ' name="%s"' % self.name
    if self.image_url:
      robot_attrs += ' imageurl="%s"' % self.image_url
    if self.profile_url:
      robot_attrs += ' profileurl="%s"' % self.profile_url
    lines.append('<w:profile%s/>' % robot_attrs)
    return ('<?xml version="1.0"?>\n'
            '<w:robot xmlns:w="http://wave.google.com/extensions/robots/1.0">\n'
            '%s\n</w:robot>\n') % ('\n'.join(lines))

  def GetProfileJson(self):
    """Returns JSON body for any profile handler.

    Returns:
      String of JSON to be sent as a response.
    """
    data = {}
    data['name'] = self.name
    data['imageUrl'] = self.image_url
    data['profileUrl'] = self.profile_url
    # TODO(davidbyttow): Remove this java nonsense.
    data['javaClass'] = 'com.google.wave.api.ParticipantProfile'
    return simplejson.dumps(data)
