#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Unit tests for the model module."""


__author__ = 'davidbyttow@google.com (David Byttow)'


import unittest

import model


class TestWaveModel(unittest.TestCase):
  """Tests the primary data structures for the wave model."""

  def setUp(self):
    wave_data = model.WaveData()
    wave_data.id = 'my-wave'
    wave_data.wavelet_ids = ['wavelet-1']
    self.test_wave_data = wave_data

    wavelet_data = model.WaveletData()
    wavelet_data.creator = 'creator@google.com'
    wavelet_data.creation_time = 100
    wavelet_data.last_modified_time = 101
    wavelet_data.participants = ['robot@google.com']
    wavelet_data.root_blip_id = 'blip-1'
    wavelet_data.wave_id = wave_data.id
    wavelet_data.wavelet_id = 'wavelet-1'
    self.test_wavelet_data = wavelet_data

    blip_data = model.BlipData()
    blip_data.blip_id = wavelet_data.root_blip_id
    blip_data.content = '<p>testing</p>'
    blip_data.contributors = [wavelet_data.creator, 'robot@google.com']
    blip_data.creator = wavelet_data.creator
    blip_data.last_modified_time = wavelet_data.last_modified_time
    blip_data.parent_blip_id = None
    blip_data.wave_id = wave_data.id
    blip_data.wavelet_id = wavelet_data.wavelet_id
    self.test_blip_data = blip_data

  def testWaveFields(self):
    w = model.Wave(self.test_wave_data)
    self.assertEquals(self.test_wave_data.id, w.GetId())
    self.assertEquals(self.test_wave_data.wavelet_ids, w.GetWaveletIds())

  def testWaveletFields(self):
    w = model.Wavelet(self.test_wavelet_data)
    self.assertEquals(self.test_wavelet_data.creator, w.GetCreator())

  def testBlipFields(self):
    b = model.Blip(self.test_blip_data, model.Document(self.test_blip_data))
    self.assertEquals(self.test_blip_data.child_blip_ids,
                      b.GetChildBlipIds())
    self.assertEquals(self.test_blip_data.contributors, b.GetContributors())
    self.assertEquals(self.test_blip_data.creator, b.GetCreator())
    self.assertEquals(self.test_blip_data.content,
                      b.GetDocument().GetText())
    self.assertEquals(self.test_blip_data.blip_id, b.GetId())
    self.assertEquals(self.test_blip_data.last_modified_time,
                      b.GetLastModifiedTime())
    self.assertEquals(self.test_blip_data.parent_blip_id,
                      b.GetParentBlipId())
    self.assertEquals(self.test_blip_data.wave_id,
                      b.GetWaveId())
    self.assertEquals(self.test_blip_data.wavelet_id,
                      b.GetWaveletId())
    self.assertEquals(True, b.IsRoot())

  def testBlipIsRoot(self):
    self.test_blip_data.parent_blip_id = 'blip-parent'
    b = model.Blip(self.test_blip_data, model.Document(self.test_blip_data))
    self.assertEquals(False, b.IsRoot())

  def testCreateEvent(self):
    data = {'type': 'WAVELET_PARTICIPANTS_CHANGED',
            'properties': {'blipId': 'blip-1'},
            'timestamp': 123,
            'modifiedBy': 'modifier@google.com'}
    event_data = model.CreateEvent(data)
    self.assertEquals(data['type'], event_data.type)
    self.assertEquals(data['properties'], event_data.properties)
    self.assertEquals(data['timestamp'], event_data.timestamp)
    self.assertEquals(data['modifiedBy'], event_data.modified_by)
