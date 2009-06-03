#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Unit tests for the robot_abstract module."""

__author__ = 'jacobly@google.com (Jacob Lee)'

import unittest

import robot_abstract

DEBUG_DATA = r'{"blips":{"map":{"wdykLROk*13":{"lastModifiedTime":1242079608457,"contributors":{"javaClass":"java.util.ArrayList","list":["davidbyttow@google.com"]},"waveletId":"conv+root","waveId":"wdykLROk*11","parentBlipId":null,"version":3,"creator":"davidbyttow@google.com","content":"\n","blipId":"wdykLROk*13","javaClass":"com.google.wave.api.impl.BlipData","annotations":{"javaClass":"java.util.ArrayList","list":[{"range":{"start":0,"javaClass":"com.google.wave.api.Range","end":1},"name":"user/e/davidbyttow@google.com","value":"David","javaClass":"com.google.wave.api.Annotation"}]},"elements":{"map":{},"javaClass":"java.util.HashMap"},"childBlipIds":{"javaClass":"java.util.ArrayList","list":[]}}},"javaClass":"java.util.HashMap"},"events":{"javaClass":"java.util.ArrayList","list":[{"timestamp":1242079611003,"modifiedBy":"davidbyttow@google.com","javaClass":"com.google.wave.api.impl.EventData","properties":{"map":{"participantsRemoved":{"javaClass":"java.util.ArrayList","list":[]},"participantsAdded":{"javaClass":"java.util.ArrayList","list":["monty@appspot.com"]}},"javaClass":"java.util.HashMap"},"type":"WAVELET_PARTICIPANTS_CHANGED"}]},"wavelet":{"lastModifiedTime":1242079611003,"title":"","waveletId":"conv+root","rootBlipId":"wdykLROk*13","javaClass":"com.google.wave.api.impl.WaveletData","dataDocuments":null,"creationTime":1242079608457,"waveId":"wdykLROk*11","participants":{"javaClass":"java.util.ArrayList","list":["davidbyttow@google.com","monty@appspot.com"]},"creator":"davidbyttow@google.com","version":5}}'


class TestHelpers(unittest.TestCase):
  """Tests for the web helper functions in abstract_robot."""

  def testParseJSONBody(self):
    context, events = robot_abstract.ParseJSONBody(DEBUG_DATA)

    # Test some basic properties; the rest should be covered by
    # ops.CreateContext.
    blips = context.GetBlips()
    self.assertEqual(1, len(blips))
    self.assertEqual('wdykLROk*13', blips[0].GetId())
    self.assertEqual('wdykLROk*11', blips[0].GetWaveId())
    self.assertEqual('conv+root', blips[0].GetWaveletId())

    self.assertEqual(1, len(events))
    event = events[0]
    self.assertEqual('WAVELET_PARTICIPANTS_CHANGED', event.type)
    self.assertEqual({'participantsRemoved': [],
                      'participantsAdded': ['monty@appspot.com']},
                     event.properties)

  def testSerializeContextSansOps(self):
    context, _ = robot_abstract.ParseJSONBody(DEBUG_DATA)
    serialized = robot_abstract.SerializeContext(context)
    self.assertEqual(
        '{"operations": {"javaClass": "java.util.ArrayList", "list": []}, '
        '"javaClass": "com.google.wave.api.impl.OperationMessageBundle"}',
        serialized)

  def testSerializeContextWithOps(self):
    context, _ = robot_abstract.ParseJSONBody(DEBUG_DATA)
    wavelet = context.GetWavelets()[0]
    blip = context.GetBlipById(wavelet.GetRootBlipId())
    blip.GetDocument().SetText('Hello, wave!')
    serialized = robot_abstract.SerializeContext(context)
    self.assertEqual(
        '{"operations": {"javaClass": "java.util.ArrayList", "list": ['
        '{"blipId": "wdykLROk*13", "index": -1, "waveletId": "conv+root", "javaClass": "com.google.wave.api.impl.OperationImpl", "waveId": "wdykLROk*11", "property": {"javaClass": "com.google.wave.api.Range", "end": 1, "start": 0}, "type": "DOCUMENT_DELETE"}, '
        '{"blipId": "wdykLROk*13", "index": 0, "waveletId": "conv+root", "javaClass": "com.google.wave.api.impl.OperationImpl", "waveId": "wdykLROk*11", "property": "Hello, wave!", "type": "DOCUMENT_INSERT"}'
        ']}, "javaClass": "com.google.wave.api.impl.OperationMessageBundle"}',
        serialized)


class TestGetCapabilitiesXml(unittest.TestCase):

  def setUp(self):
    self.robot = robot_abstract.Robot('Testy')

  def assertStringsEqual(self, s1, s2):
    self.assertEqual(s1, s2, 'Strings differ:\n%s--\n%s' % (s1, s2))

  def testDefault(self):
    expected = (
        '<?xml version="1.0"?>\n'
        '<w:robot xmlns:w="http://wave.google.com/extensions/robots/1.0">\n'
        '<w:capabilities>\n</w:capabilities>\n'
        '<w:profile name="Testy"/>\n'
        '</w:robot>\n')
    xml = self.robot.GetCapabilitiesXml()
    self.assertStringsEqual(expected, xml)

  def testUrls(self):
    profile_robot = robot_abstract.Robot(
        'Testy', image_url='http://example.com/image.png',
        profile_url='http://example.com/profile.xml')
    expected = (
        '<?xml version="1.0"?>\n'
        '<w:robot xmlns:w="http://wave.google.com/extensions/robots/1.0">\n'
        '<w:capabilities>\n</w:capabilities>\n'
        '<w:profile name="Testy"'
        ' imageurl="http://example.com/image.png"'
        ' profileurl="http://example.com/profile.xml"/>\n'
        '</w:robot>\n')
    xml = profile_robot.GetCapabilitiesXml()
    self.assertStringsEqual(expected, xml)

  def testCapsAndEvents(self):
    self.robot.RegisterHandler('myevent', None)
    self.robot.RegisterCronJob('/ping', 20)
    expected = (
        '<?xml version="1.0"?>\n'
        '<w:robot xmlns:w="http://wave.google.com/extensions/robots/1.0">\n'
        '<w:capabilities>\n'
        '  <w:capability name="myevent"/>\n'
        '</w:capabilities>\n'
        '<w:crons>\n  <w:cron path="/ping" timerinseconds="20"/>\n</w:crons>\n'
        '<w:profile name="Testy"/>\n'
        '</w:robot>\n')
    xml = self.robot.GetCapabilitiesXml()
    self.assertStringsEqual(expected, xml)


if __name__ == '__main__':
  unittest.main()
