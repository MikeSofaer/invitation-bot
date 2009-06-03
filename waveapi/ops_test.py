#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Unit tests for the ops module."""


__author__ = 'davidbyttow@google.com (David Byttow)'


import unittest

import document
import model
import ops


class TestOperation(unittest.TestCase):
  """Test case for Operation class."""

  def testDefaults(self):
    op = ops.Operation(ops.WAVELET_APPEND_BLIP, 'wave-id', 'wavelet-id')
    self.assertEquals(ops.WAVELET_APPEND_BLIP, op.type)
    self.assertEquals('wave-id', op.wave_id)
    self.assertEquals('wavelet-id', op.wavelet_id)
    self.assertEquals('', op.blip_id)
    self.assertEquals(-1, op.index)
    self.assertEquals(None, op.property)

  def testFields(self):
    op = ops.Operation(ops.DOCUMENT_INSERT, 'wave-id', 'wavelet-id',
                       blip_id='blip-id',
                       index=1,
                       prop='foo')
    self.assertEquals(ops.DOCUMENT_INSERT, op.type)
    self.assertEquals('wave-id', op.wave_id)
    self.assertEquals('wavelet-id', op.wavelet_id)
    self.assertEquals('blip-id', op.blip_id)
    self.assertEquals(1, op.index)
    self.assertEquals('foo', op.property)


class TestOpBasedClasses(unittest.TestCase):
  """Base class for op-based test classes. Sets up some test data."""

  def setUp(self):
    self.test_context = ops._ContextImpl()

    wave_data = model.WaveData()
    wave_data.id = 'my-wave'
    wave_data.wavelet_ids = set(['wavelet-1'])
    self.test_wave_data = wave_data
    self.test_wave = self.test_context.AddWave(wave_data)

    wavelet_data = model.WaveletData()
    wavelet_data.creator = 'creator@google.com'
    wavelet_data.creation_time = 100
    wavelet_data.last_modified_time = 101
    wavelet_data.participants = set(['robot@google.com'])
    wavelet_data.root_blip_id = 'blip-1'
    wavelet_data.wave_id = wave_data.id
    wavelet_data.wavelet_id = 'wavelet-1'
    self.test_wavelet_data = wavelet_data
    self.test_wavelet = self.test_context.AddWavelet(wavelet_data)

    blip_data = model.BlipData()
    blip_data.blip_id = wavelet_data.root_blip_id
    blip_data.content = '<p>testing</p>'
    blip_data.contributors = set([wavelet_data.creator, 'robot@google.com'])
    blip_data.creator = wavelet_data.creator
    blip_data.last_modified_time = wavelet_data.last_modified_time
    blip_data.parent_blip_id = None
    blip_data.wave_id = wave_data.id
    blip_data.wavelet_id = wavelet_data.wavelet_id
    self.test_blip_data = blip_data
    self.test_blip = self.test_context.AddBlip(blip_data)


class TestOpBasedContext(TestOpBasedClasses):
  """Test case for testing the operation-based context class, _ContextImpl."""

  def testVerifySetup(self):
    self.assertEquals(self.test_wave_data,
                      self.test_context.GetWaveById('my-wave')._data)
    self.assertEquals(self.test_wavelet_data,
                      self.test_context.GetWaveletById('wavelet-1')._data)
    self.assertEquals(self.test_blip_data,
                      self.test_context.GetBlipById('blip-1')._data)

  def testRemove(self):
    self.test_context.RemoveWave('my-wave')
    self.assertEquals(None, self.test_context.GetWaveById('my-wave'))
    self.test_context.RemoveWavelet('wavelet-1')
    self.assertEquals(None, self.test_context.GetWaveletById('wavelet-1'))
    self.test_context.RemoveBlip('blip-1')
    self.assertEquals(None, self.test_context.GetBlipById('blip-1'))


class TestOpBasedWave(TestOpBasedClasses):
  """Test case for OpBasedWave class."""

  def testCreateWavelet(self):
    self.assertRaises(NotImplementedError,
                      self.test_wave.CreateWavelet)


class TestOpBasedWavelet(TestOpBasedClasses):
  """Test case for OpBasedWavelet class."""

  def testCreateBlip(self):
    blip = self.test_wavelet.CreateBlip()
    self.assertEquals('my-wave', blip.GetWaveId())
    self.assertEquals('wavelet-1', blip.GetWaveletId())
    self.assertTrue(blip.GetId().startswith('TBD'))
    self.assertEquals(blip, self.test_context.GetBlipById(blip.GetId()))

  def testAddParticipant(self):
    p = 'newguy@google.com'
    self.test_wavelet.AddParticipant(p)
    self.assertTrue(p in self.test_wavelet.GetParticipants())

  def testRemoveSelf(self):
    self.assertRaises(NotImplementedError,
                      self.test_wavelet.RemoveSelf)

  def testSetDataDocument(self):
    self.test_wavelet.SetDataDocument('key', 'value')
    self.assertEquals('value', self.test_wavelet.GetDataDocument('key'))

  def testSetTitle(self):
    self.assertRaises(NotImplementedError,
                      self.test_wavelet.SetTitle, 'foo')


class TestOpBasedBlip(TestOpBasedClasses):
  """Test case for OpBasedBlip class."""

  def testCreateChild(self):
    blip = self.test_blip.CreateChild()
    self.assertEquals('my-wave', blip.GetWaveId())
    self.assertEquals('wavelet-1', blip.GetWaveletId())
    self.assertTrue(blip.GetId().startswith('TBD'))
    self.assertEquals(blip, self.test_context.GetBlipById(blip.GetId()))

  def testDelete(self):
    self.test_blip.Delete()
    self.assertEquals(None,
                      self.test_context.GetBlipById(self.test_blip.GetId()))


class TestOpBasedDocument(TestOpBasedClasses):
  """Test case for OpBasedDocument class."""

  def setUp(self):
    super(TestOpBasedDocument, self).setUp()
    self.test_doc = self.test_blip.GetDocument()
    self.test_doc.SetText('123456')

  def testSetText(self):
    text = 'Hello test.'
    self.assertTrue(self.test_doc.GetText() != text)
    self.test_doc.SetText(text)
    self.assertEquals(text, self.test_doc.GetText())

  def testSetTextInRange(self):
    text = 'abc'
    self.test_doc.SetTextInRange(document.Range(0, 2), text)
    self.assertEquals('abc456', self.test_doc.GetText())
    self.test_doc.SetTextInRange(document.Range(2, 2), text)
    self.assertEquals('ababc456', self.test_doc.GetText())

  def testAppendText(self):
    text = '789'
    self.test_doc.AppendText(text)
    self.assertEquals('123456789', self.test_doc.GetText())

  def testClear(self):
    self.test_doc.Clear()
    self.assertEquals('', self.test_doc.GetText())

  def testDeleteRange(self):
    self.test_doc.DeleteRange(document.Range(0, 1))
    self.assertEquals('3456', self.test_doc.GetText())
    self.test_doc.DeleteRange(document.Range(0, 0))
    self.assertEquals('456', self.test_doc.GetText())

  def testAnnotateDocument(self):
    self.test_doc.AnnotateDocument('key', 'value')
    self.assertTrue(self.test_doc.HasAnnotation('key'))
    self.assertFalse(self.test_doc.HasAnnotation('non-existent-key'))

  def testSetAnnotation(self):
    self.test_doc.SetAnnotation(document.Range(0, 1), 'key', 'value')
    self.assertTrue(self.test_doc.HasAnnotation('key'))

  def testDeleteAnnotationByName(self):
    self.assertRaises(NotImplementedError,
                      self.test_doc.DeleteAnnotationsByName, 'key')

  def testDeleteAnnotationInRange(self):
    self.assertRaises(NotImplementedError,
                      self.test_doc.DeleteAnnotationsInRange,
                      document.Range(0, 1), 'key')

  def testAppendInlineBlip(self):
    blip = self.test_doc.AppendInlineBlip()
    self.assertEquals('my-wave', blip.GetWaveId())
    self.assertEquals('wavelet-1', blip.GetWaveletId())
    self.assertTrue(blip.GetId().startswith('TBD'))
    self.assertEquals(self.test_blip.GetId(), blip.GetParentBlipId())
    self.assertEquals(blip, self.test_context.GetBlipById(blip.GetId()))

  def testDeleteInlineBlip(self):
    blip = self.test_doc.AppendInlineBlip()
    self.test_doc.DeleteInlineBlip(blip.GetId())
    self.assertEquals(None, self.test_context.GetBlipById(blip.GetId()))

  def testInsertInlineBlip(self):
    blip = self.test_doc.InsertInlineBlip(1)
    self.assertEquals('my-wave', blip.GetWaveId())
    self.assertEquals('wavelet-1', blip.GetWaveletId())
    self.assertTrue(blip.GetId().startswith('TBD'))
    self.assertEquals(self.test_blip.GetId(), blip.GetParentBlipId())
    self.assertEquals(blip, self.test_context.GetBlipById(blip.GetId()))

  def testAppendElement(self):
    self.test_doc.AppendElement("GADGET")




