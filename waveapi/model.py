#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines classes that represent parts of the common wave model.

Defines the core data structures for the common wave model. At this level,
models are read-only but can be modified through operations.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


import document
import logging


ROOT_WAVELET_ID_SUFFIX = '!conv+root'


class WaveData(object):
  """Defines the data for a single wave."""

  def __init__(self):
    self.id = None
    self.wavelet_ids = set()


class Wave(object):
  """Models a single wave instance.

  A single wave is composed of its id and any wavelet ids that belong to it.
  """

  def __init__(self, data):
    """Inits this wave with its data.

    Args:
      data: A WaveData instance.
    """

    self._data = data

  def GetId(self):
    """Returns this wave's id."""
    return self._data.id

  def GetWaveletIds(self):
    """Returns a set of wavelet ids."""
    return self._data.wavelet_ids


class WaveletData(object):
  """Defines the data for a single wavelet."""

  java_class = 'com.google.wave.api.impl.WaveletData'

  def __init__(self):
    self.creator = None
    self.creation_time = 0
    self.data_documents = {}
    self.last_modifed_time = 0
    self.participants = set()
    self.root_blip_id = None
    self.title = ''
    self.version = 0
    self.wave_id = None
    self.wavelet_id = None


class Wavelet(object):
  """Models a single wavelet instance.

  A single wavelet is composed of metadata, participants and the blips it
  contains.
  """

  def __init__(self, data):
    """Inits this wavelet with its data.

    Args:
      data: A WaveletData instance.
    """
    self._data = data

  def GetCreator(self):
    """Returns the participant id of the creator of this wavelet."""
    return self._data.creator

  def GetCreationTime(self):
    """Returns the time that this wavelet was first created in milliseconds."""
    return self._data.creation_time

  def GetDataDocument(self, name, default=None):
    """Returns a data document for this wavelet based on key name."""
    return self._data.data_documents.get(name, default)

  def GetId(self):
    """Returns this wavelet's id."""
    return self._data.wavelet_id

  def GetLastModifiedTime(self):
    """Returns the time that this wavelet was last modified in milliseconds."""
    return self._data.last_modified_time

  def GetParticipants(self):
    """Returns a set of participants on this wavelet."""
    return self._data.participants

  def GetRootBlipId(self):
    """Returns this wavelet's root blip id."""
    return self._data.root_blip_id

  def GetTitle(self):
    """Returns the title of this wavelet."""
    return self._data.title

  def GetWaveId(self):
    """Returns this wavelet's parent wave id."""
    return self._data.wave_id


class BlipData(object):
  """Data that describes a single blip."""

  java_class = 'com.google.wave.api.impl.BlipData'

  def __init__(self):
    self.annotations = []
    self.blip_id = None
    self.child_blip_ids = set()
    self.content = ''
    self.contributors = set()
    self.creator = None
    self.elements = {}
    self.last_modified_time = 0
    self.parent_blip_id = None
    self.version = -1
    self.wave_id = None
    self.wavelet_id = None


class Blip(object):
  """Models a single blip instance.

  Blips are essentially elements of conversation. Blips can live in a
  hierarchy of blips. A root blip has no parent blip id, but all blips
  have the ids of the wave and wavelet that they are associated with.

  Blips also contain annotations, content and elements, which are accessed via
  the Document object.
  """

  def __init__(self, data, doc):
    """Inits this blip with its data and document view.

    Args:
      data: A BlipData instance.
      doc: A Document instance associated with this blip.
    """
    self._data = data
    self._document = doc

  def GetChildBlipIds(self):
    """Returns a set of blip ids that are children of this blip."""
    return self._data.child_blip_ids

  def GetContributors(self):
    """Returns a set of participant ids that contributed to this blip."""
    return self._data.contributors

  def GetCreator(self):
    """Returns the id of the participant that created this blip."""
    return self._data.creator

  def GetDocument(self):
    """Returns the Document of this blip, which contains content data."""
    return self._document

  def GetId(self):
    """Returns the id of this blip."""
    return self._data.blip_id

  def GetLastModifiedTime(self):
    """Returns the time that this blip was last modified by the server."""
    return self._data.last_modified_time

  def GetParentBlipId(self):
    """Returns the id of this blips parent or None if it is the root."""
    return self._data.parent_blip_id

  def GetWaveId(self):
    """Returns the id of the wave that this blip belongs to."""
    return self._data.wave_id

  def GetWaveletId(self):
    """Returns the id of the wavelet that this blip belongs to."""
    return self._data.wavelet_id

  def IsRoot(self):
    """Returns True if this is the root blip of a wavelet."""
    return self._data.parent_blip_id is None


class Document(object):
  """Base representation of a document of a blip.

  TODO(davidbyttow): Add support for annotations and elements.
  """

  def __init__(self, blip_data):
    """Inits this document with the data of the blip it is representing.

    Args:
      blip_data: A BlipData instance.
    """
    self._blip_data = blip_data

  def GetText(self):
    """Returns the raw text content of this document."""
    return self._blip_data.content


class Event(object):
  """Data describing a single event."""

  def __init__(self):
    self.type = ''
    self.timestamp = 0
    self.modified_by = ''
    self.properties = {}


def CreateEvent(data):
  """Construct event data from the raw incoming wire protocol."""
  event = Event()
  event.type = data['type']
  event.timestamp = data['timestamp']
  event.modified_by = data['modifiedBy']
  event.properties = data['properties'] or {}
  return event


def CreateWaveletData(data):
  """Construct wavelet data from the raw incoming wire protocol.

  TODO(davidbyttow): Automate this based on naming like the Serialize methods.

  Args:
    data: Serialized data from server.

  Returns:
    Instance of WaveletData based on the fields.
  """
  wavelet_data = WaveletData()
  wavelet_data.creator = data['creator']
  wavelet_data.creation_time = data['creationTime']
  wavelet_data.data_documents = data['dataDocuments'] or {}
  wavelet_data.last_modified_time = data['lastModifiedTime']
  wavelet_data.participants = set(data['participants'])
  wavelet_data.root_blip_id = data['rootBlipId']
  wavelet_data.title = data['title']
  wavelet_data.version = data['version']
  wavelet_data.wave_id = data['waveId']
  wavelet_data.wavelet_id = data['waveletId']
  return wavelet_data


def CreateBlipData(data):
  """Construct blip data from the raw incoming wire protocol.

  TODO(davidbyttow): Automate this based on naming like the Serialize methods.

  Args:
    data: Serialized data from server.

  Returns:
    Instance of BlipData based on the fields.
  """
  blip_data = BlipData()
  blip_data.annotations = []
  for annotation in data['annotations']:
    r = document.Range(annotation['range']['start'],
                       annotation['range']['end'])
    blip_data.annotations.append(document.Annotation(annotation['name'],
                                                     annotation['value'],
                                                     r=r))
  blip_data.child_blip_ids = set(data['childBlipIds'])
  blip_data.content = data['content']
  blip_data.contributors = set(data['contributors'])
  blip_data.creator = data['creator']
  blip_data.elements = data['elements']
  blip_data.last_modified_time = data['lastModifiedTime']
  blip_data.parent_blip_id = data['parentBlipId']
  blip_data.blip_id = data['blipId']
  blip_data.version = data['version']
  blip_data.wave_id = data['waveId']
  blip_data.wavelet_id = data['waveletId']
  return blip_data


class Context(object):
  """Contains information associated with a single request from the server.

  This includes the current waves in this session
  and any operations that have been enqueued during request processing.
  """

  def __init__(self):
    self._waves = {}
    self._wavelets = {}
    self._blips = {}
    self._operations = []

  def GetBlipById(self, blip_id):
    """Returns a blip by id or None if it does not exist."""
    return self._blips.get(blip_id, None)

  def GetWaveById(self, wave_id):
    """Returns a wave by id or None if it does not exist."""
    return self._waves.get(wave_id, None)

  def GetWaveletById(self, wavelet_id):
    """Returns a wavelet by id or None if it does not exist."""
    return self._wavelets.get(wavelet_id, None)

  def GetRootWavelet(self):
    """Returns the root wavelet or None if it is not in this context."""
    for wavelet in self._wavelets.values():
      wavelet_id = wavelet.GetId()
      if wavelet_id.endswith(ROOT_WAVELET_ID_SUFFIX):
        return wavelet
    logging.warning("Could not retrieve root wavelet.")
    return None

  def GetWaves(self):
    """Returns the list of waves associated with this session."""
    return self._waves.values()

  def GetWavelets(self):
    """Returns the list of wavelets associated with this session."""
    return self._wavelets.values()

  def GetBlips(self):
    """Returns the list of blips associated with this session."""
    return self._blips.values()
