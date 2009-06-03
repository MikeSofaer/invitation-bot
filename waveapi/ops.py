#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Support for operations that can be applied to the server.

Contains classes and utilities for creating operations that are to be
applied on the server.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'


import random

import document
import model
import util


# Operation Types
WAVELET_APPEND_BLIP = 'WAVELET_APPEND_BLIP'
WAVELET_ADD_PARTICIPANT = 'WAVELET_ADD_PARTICIPANT'
WAVELET_CREATE = 'WAVELET_CREATE'
WAVELET_REMOVE_SELF = 'WAVELET_REMOVE_SELF'
WAVELET_DATADOC_SET = 'WAVELET_DATADOC_SET'
WAVELET_SET_TITLE = 'WAVELET_SET_TITLE'
BLIP_CREATE_CHILD = 'BLIP_CREATE_CHILD'
BLIP_DELETE = 'BLIP_DELETE'
DOCUMENT_ANNOTATION_DELETE = 'DOCUMENT_ANNOTATION_DELETE'
DOCUMENT_ANNOTATION_SET = 'DOCUMENT_ANNOTATION_SET'
DOCUMENT_ANNOTATION_SET_NORANGE = 'DOCUMENT_ANNOTATION_SET_NORANGE'
DOCUMENT_APPEND = 'DOCUMENT_APPEND'
DOCUMENT_APPEND_STYLED_TEXT = 'DOCUMENT_APPEND_STYLED_TEXT'
DOCUMENT_INSERT = 'DOCUMENT_INSERT'
DOCUMENT_DELETE = 'DOCUMENT_DELETE'
DOCUMENT_REPLACE = 'DOCUMENT_REPLACE'
DOCUMENT_ELEMENT_APPEND = 'DOCUMENT_ELEMENT_APPEND'
DOCUMENT_ELEMENT_DELETE = 'DOCUMENT_ELEMENT_DELETE'
DOCUMENT_ELEMENT_INSERT = 'DOCUMENT_ELEMENT_INSERT'
DOCUMENT_ELEMENT_INSERT_AFTER = 'DOCUMENT_ELEMENT_INSERT_AFTER'
DOCUMENT_ELEMENT_INSERT_BEFORE = 'DOCUMENT_ELEMENT_INSERT_BEFORE'
DOCUMENT_ELEMENT_REPLACE = 'DOCUMENT_ELEMENT_REPLACE'
DOCUMENT_INLINE_BLIP_APPEND = 'DOCUMENT_INLINE_BLIP_APPEND'
DOCUMENT_INLINE_BLIP_DELETE = 'DOCUMENT_INLINE_BLIP_DELETE'
DOCUMENT_INLINE_BLIP_INSERT = 'DOCUMENT_INLINE_BLIP_INSERT'
DOCUMENT_INLINE_BLIP_INSERT_AFTER_ELEMENT = ('DOCUMENT_INLINE_BLIP_INSERT_'
                                             'AFTER_ELEMENT')


class Operation(object):
  """Represents a generic operation applied on the server.

  This operation class contains data that is filled in depending on the
  operation type.

  It can be used directly, but doing so will not result
  in local, transient reflection of state on the blips. In other words,
  creating a "delete blip" operation will not remove the blip from the local
  context for the duration of this session. It is better to use the OpBased
  model classes directly instead.
  """

  java_class = 'com.google.wave.api.impl.OperationImpl'

  def __init__(self, op_type, wave_id, wavelet_id, blip_id='', index=-1,
               prop=None):
    """Initializes this operation with contextual data.

    Args:
      op_type: Type of operation.
      wave_id: The id of the wave that this operation is to be applied.
      wavelet_id: The id of the wavelet that this operation is to be applied.
      blip_id: The optional id of the blip that this operation is to be applied.
      index: Optional integer index for content-based operations.
      prop: A weakly typed property object is based on the context of this
          operation.
    """
    self.type = op_type
    self.wave_id = wave_id
    self.wavelet_id = wavelet_id
    self.blip_id = blip_id
    self.index = index
    self.property = prop


class OpBasedWave(model.Wave):
  """Subclass of the wave model capable of generating operations.

  Any mutation-based methods will likely result in one or more operations
  being applied locally and sent to the server.
  """

  def __init__(self, data, context):
    """Initializes this wave with the session context."""
    super(OpBasedWave, self).__init__(data)
    self.__context = context

  def CreateWavelet(self):
    """Creates a new wavelet on this wave."""
    self.__context.builder.WaveletCreate(self.GetId())


class OpBasedWavelet(model.Wavelet):
  """Subclass of the wavelet model capable of generating operations.

  Any mutation-based methods will likely result in one or more operations
  being applied locally and sent to the server.
  """

  def __init__(self, data, context):
    """Initializes this wavelet with the session context."""
    super(OpBasedWavelet, self).__init__(data)
    self.__context = context

  def CreateBlip(self):
    """Creates and appends a blip to this wavelet and returns it.

    Returns:
      A transient version of the blip that was created.
    """
    blip_data = self.__context.builder.WaveletAppendBlip(self.GetWaveId(),
                                                         self.GetId())
    return self.__context.AddBlip(blip_data)

  def AddParticipant(self, participant_id):
    """Adds a participant to a wavelet.

    Args:
      participant_id: Id of the participant that is to be added.
    """
    self.__context.builder.WaveletAddParticipant(self.GetWaveId(), self.GetId(),
                                                 participant_id)
    self._data.participants.add(participant_id)

  def RemoveSelf(self):
    """Removes this robot from the wavelet."""
    self.__context.builder.WaveletRemoveSelf(self.GetWaveId(), self.GetId())
    # TODO(davidbyttow): Locally remove the robot.

  def SetDataDocument(self, name, data):
    """Sets a key/value pair on the wavelet data document.

    Args:
      name: The string key.
      data: The value associated with this key.
    """
    self.__context.builder.WaveletSetDataDoc(self.GetWaveId(), self.GetId(),
                                             name, data)
    self._data.data_documents[name] = data

  def SetTitle(self, title):
    """Sets the title of this wavelet.

    Args:
      title: String title to for this wave.
    """
    self.__context.builder.WaveletSetTitle(self.GetWaveId(), self.GetId(),
                                           title)
    self.__data.title = title


class OpBasedBlip(model.Blip):
  """Subclass of the blip model capable of generating operations.

  Any mutation-based methods will likely result in one or more operations
  being applied locally and sent to the server.
  """

  def __init__(self, data, context):
    """Initializes this blip with the session context."""
    super(OpBasedBlip, self).__init__(data, OpBasedDocument(data, context))
    self.__context = context

  def CreateChild(self):
    """Creates a child blip of this blip."""
    blip_data = self.__context.builder.BlipCreateChild(self.GetWaveId(),
                                                       self.GetWaveletId(),
                                                       self.GetId())
    return self.__context.AddBlip(blip_data)

  def Delete(self):
    """Deletes this blip from the wavelet."""
    self.__context.builder.BlipDelete(self.GetWaveId(),
                                      self.GetWaveletId(),
                                      self.GetId())
    return self.__context.RemoveBlip(self.GetId())


class OpBasedDocument(model.Document):
  """Subclass of the document model capable of generating operations.

  Any mutation-based methods will likely result in one or more operations
  being applied locally and sent to the server.

  TODO(davidbyttow): Manage annotations and elements as content is updated.
  """

  def __init__(self, blip_data, context):
    """Initializes this document with its owning blip and session context."""
    super(OpBasedDocument, self).__init__(blip_data)
    self.__context = context

  def HasAnnotation(self, name):
    """Determines if given named annotation is anywhere on this document.

    Args:
      name: The key name of the annotation.

    Returns:
      True if the annotation exists.
    """
    for annotation in self._blip_data.annotations:
      if annotation.name == name:
        return True
    return False

  def SetText(self, text):
    """Clears and sets the text of this document.

    Args:
      text: The text content to replace this document with.
    """
    self.Clear()
    self.__context.builder.DocumentInsert(self._blip_data.wave_id,
                                          self._blip_data.wavelet_id,
                                          self._blip_data.blip_id,
                                          text)
    self._blip_data.content = text

  def SetTextInRange(self, r, text):
    """Deletes text within a range and sets the supplied text in its place.

    Args:
      r: Range to delete and where to set the new text.
      text: The text to set at the range start position.
    """
    self.DeleteRange(r)
    self.InsertText(r.start, text)

  def InsertText(self, start, text):
    """Inserts text at a specific position.

    Args:
      start: The index position where to set the text.
      text: The text to set.
    """
    self.__context.builder.DocumentInsert(self._blip_data.wave_id,
                                          self._blip_data.wavelet_id,
                                          self._blip_data.blip_id,
                                          text, index=start)
    left = self._blip_data.content[:start]
    right = self._blip_data.content[start:]
    self._blip_data.content = left + text + right

  def AppendText(self, text):
    """Appends text to the end of this document.

    Args:
      text: The text to append.
    """
    self.__context.builder.DocumentAppend(self._blip_data.wave_id,
                                          self._blip_data.wavelet_id,
                                          self._blip_data.blip_id,
                                          text)
    self._blip_data.content += text

  def Clear(self):
    """Clears the content of this document."""
    self.__context.builder.DocumentDelete(self._blip_data.wave_id,
                                          self._blip_data.wavelet_id,
                                          self._blip_data.blip_id,
                                          0, len(self._blip_data.content))
    self._blip_data.content = ''

  def DeleteRange(self, r):
    """Deletes the content in the specified range.

    Args:
      r: A Range instance specifying the range to delete.
    """
    self.__context.builder.DocumentDelete(self._blip_data.wave_id,
                                          self._blip_data.wavelet_id,
                                          self._blip_data.blip_id,
                                          r.start, r.end)
    left = self._blip_data.content[:r.start]
    right = self._blip_data.content[r.end + 1:]
    self._blip_data.content = left + right

  def AnnotateDocument(self, name, value):
    """Annotates the entire document.

    Args:
      name: A string as the key for this annotation.
      value: The value of this annotation.
    """
    b = self.__context.builder
    b.DocumentAnnotationSetNoRange(self._blip_data.wave_id,
                                   self._blip_data.wavelet_id,
                                   self._blip_data.blip_id,
                                   name, value)
    r = document.Range(0, len(self._blip_data.content))
    self._blip_data.annotations.append(document.Annotation(name, value, r))

  def SetAnnotation(self, r, name, value):
    """Sets an annotation on a given range.

    Args:
      r: A Range specifying the range to set the annotation.
      name: A string as the key for this annotation.
      value: The value of this annotaton.
    """
    self.__context.builder.DocumentAnnotationSet(self._blip_data.wave_id,
                                                 self._blip_data.wavelet_id,
                                                 self._blip_data.blip_id,
                                                 r.start, r.end,
                                                 name, value)
    self._blip_data.annotations.append(document.Annotation(name, value, r))

  def DeleteAnnotationsByName(self, name):
    """Deletes all annotations with a given key name.

    Args:
      name: A string as the key for the annotation to delete.
    """
    size = len(self._blip_data.content)
    self.__context.builder.DocumentAnnotationDelete(self._blip_data.wave_id,
                                                    self._blip_data.wavelet_id,
                                                    self._blip_data.blip_id,
                                                    0, size, name)
    for index in range(len(self._blip_data.annotations)):
      annotation = self._blip_data.annotations[index]
      if annotation.name == name:
        del self._blip_data.annotations[index]

  def DeleteAnnotationsInRange(self, r, name):
    """Clears all of the annotations within a given range with a given key.

    Args:
      r: A Range specifying the range to delete.
      name: Annotation key type to clear.
    """
    self.__context.builder.DocumentAnnotationDelete(self._blip_data.wave_id,
                                                    self._blip_data.wavelet_id,
                                                    self._blip_data.blip_id,
                                                    r.start, r.end,
                                                    name)
    # TODO(davidbyttow): split local annotations.

  def AppendInlineBlip(self):
    """Appends an inline blip to this blip.

    Returns:
      The local blip that was appended.
    """
    blip_data = self.__context.builder.DocumentInlineBlipAppend(
        self._blip_data.wave_id, self._blip_data.wavelet_id,
        self._blip_data.blip_id)
    return self.__context.AddBlip(blip_data)

  def DeleteInlineBlip(self, inline_blip_id):
    """Deletes an inline blip from this blip.

    Args:
      inline_blip_id: The id of the blip to remove.
    """
    self.__context.builder.DocumentInlineBlipDelete(self._blip_data.wave_id,
                                                    self._blip_data.wavelet_id,
                                                    self._blip_data.blip_id,
                                                    inline_blip_id)
    self.__context.RemoveBlip(inline_blip_id)

  def InsertInlineBlip(self, position):
    """Inserts an inline blip into this blip at a specific position.

    Args:
      position: Position to insert the blip at.

    Returns:
      The BlipData of the blip that was created.
    """
    blip_data = self.__context.builder.DocumentInlineBlipInsert(
        self._blip_data.wave_id,
        self._blip_data.wavelet_id,
        self._blip_data.blip_id,
        position)
    # TODO(davidbyttow): Add local blip element.
    return self.__context.AddBlip(blip_data)

  def DeleteElement(self, position):
    """Deletes an Element at a given position.

    Args:
      position: Position of the Element to delete.
    """
    self.__context.builder.DocumentElementDelete(self._blip_data.wave_id,
                                                 self._blip_data.wavelet_id,
                                                 self._blip_data.blip_id,
                                                 position)

  def InsertElement(self, position, element):
    """Inserts an Element at a given position.

    Args:
      position: Position of the element to replace.
      element: The Element to replace with.
    """
    self.__context.builder.DocumentElementInsert(self._blip_data.wave_id,
                                                 self._blip_data.wavelet_id,
                                                 self._blip_data.blip_id,
                                                 position, element)

  def ReplaceElement(self, position, element):
    """Replaces an Element at a given position with a new element.

    Args:
      position: Position of the element to replace.
      element: The Element to replace with.
    """
    self.__context.builder.DocumentElementReplace(self._blip_data.wave_id,
                                                  self._blip_data.wavelet_id,
                                                  self._blip_data.blip_id,
                                                  position, element)

  def AppendElement(self, element):
    self.__context.builder.DocumentElementAppend(self._blip_data.wave_id,
                                                 self._blip_data.wavelet_id,
                                                 self._blip_data.blip_id,
                                                 element)


class _ContextImpl(model.Context):
  """An internal implementation of the Context class.

  This implementation of the context is capable of adding waves, wavelets
  and blips to itself. This is useful when applying operations locally
  in a single session. Through this, clients can access waves, wavelets and
  blips and add operations to be applied to those objects by the server.

  Operations are applied in the order that they are received. Adding
  operations manually will not be reflected in the state of the context.
  """

  def __init__(self):
    super(_ContextImpl, self).__init__()
    self.builder = OpBuilder(self)

  def AddOperation(self, op):
    """Adds an operation to the list of operations to applied by the server.

    After all events are handled, the operation list is sent back to the server
    and applied in order. Adding an operation this way will have no effect
    on the state of the context or its entities.

    Args:
      op: An instance of an Operation.
    """
    self._operations.append(op)

  def AddWave(self, wave_data):
    """Adds a transient wave based on the data supplied.

    Args:
      wave_data: An instance of WaveData describing this wave.

    Returns:
      An OpBasedWave that may have operations applied to it.
    """
    wave = OpBasedWave(wave_data, self)
    self._waves[wave.GetId()] = wave
    return wave

  def AddWavelet(self, wavelet_data):
    """Adds a transient wavelet based on the data supplied.

    Args:
      wavelet_data: An instance of WaveletData describing this wavelet.

    Returns:
      An OpBasedWavelet that may have operations applied to it.
    """
    wavelet = OpBasedWavelet(wavelet_data, self)
    self._wavelets[wavelet.GetId()] = wavelet
    return wavelet

  def AddBlip(self, blip_data):
    """Adds a transient blip based on the data supplied.

    Args:
      blip_data: An instance of BlipData describing this blip.

    Returns:
      An OpBasedBlip that may have operations applied to it.
    """
    blip = OpBasedBlip(blip_data, self)
    self._blips[blip.GetId()] = blip
    return blip

  def RemoveWave(self, wave_id):
    """Removes a wave locally."""
    if wave_id in self._waves:
      del self._waves[wave_id]

  def RemoveWavelet(self, wavelet_id):
    """Removes a wavelet locally."""
    if wavelet_id in self._wavelets:
      del self._wavelets[wavelet_id]

  def RemoveBlip(self, blip_id):
    """Removes a blip locally."""
    if blip_id in self._blips:
      del self._blips[blip_id]

  def Serialize(self):
    """Serialize the operation bundle.

    Returns:
      Dict representing this object.
    """
    data = {
        'javaClass': 'com.google.wave.api.impl.OperationMessageBundle',
        'operations': util.Serialize(self._operations)
    }
    return data


def CreateContext(data):
  """Creates a Context instance from raw data supplied by the server.

  Args:
    data: Raw data decoded from JSON sent by the server.

  Returns:
    A Context instance for this session.
  """
  context = _ContextImpl()
  for raw_blip_data in data['blips'].values():
    blip_data = model.CreateBlipData(raw_blip_data)
    context.AddBlip(blip_data)

  # Currently only one wavelet is sent.
  wavelet_data = model.CreateWaveletData(data['wavelet'])
  context.AddWavelet(wavelet_data)

  # Waves are not sent over the wire, but we can build the list based on the
  # wave ids of the wavelets.
  wave_wavelet_map = {}
  wavelets = context.GetWavelets()
  for wavelet in wavelets:
    wave_id = wavelet.GetWaveId()
    wavelet_id = wavelet.GetId()
    if wave_id not in wave_wavelet_map:
      wave_wavelet_map[wave_id] = []
    wave_wavelet_map[wave_id].append(wavelet_id)

  for wave_id, wavelet_ids in wave_wavelet_map.iteritems():
    wave_data = model.WaveData()
    wave_data.wave_id = wave_id
    wave_data.wavelet_ids = set(wavelet_ids)
    context.AddWave(wave_data)

  return context


class OpBuilder(object):
  """Wraps all currently supportable operations as functions.

  The operation builder wraps single operations as functions and generates
  operations in-order on its context. This should only be used when the context
  is not available on a specific entity. For example, to modify a blip that
  does not exist in the current context, you might specify the wave, wavelet
  and blip id to generate an operation.

  Any calls to this will not reflect the local context state in any way.
  For example, calling WaveletAppendBlip will not result in a new blip
  being added to the local context, only an operation to be applied on the
  server.
  """

  def __init__(self, context):
    """Initializes the op builder with the context.

    Args:
      context: A Context instance to generate operations on.
    """
    self.__context = context

  def __CreateNewBlipData(self, wave_id, wavelet_id):
    """Creates an ephemeral BlipData instance used for this session."""
    blip_data = model.BlipData()
    blip_data.wave_id = wave_id
    blip_data.wavelet_id = wavelet_id
    blip_data.blip_id = 'TBD_' + str(random.random()).split('.')[1]
    return blip_data

  def WaveletAppendBlip(self, wave_id, wavelet_id):
    """Requests to append a blip to a wavelet.

    Args:
      wave_id: The wave id owning the containing wavelet.
      wavelet_id: The wavelet id that this blip should be appended to.

    Returns:
      A BlipData instance representing the id information of the new blip.
    """
    blip_data = self.__CreateNewBlipData(wave_id, wavelet_id)
    op = Operation(WAVELET_APPEND_BLIP, wave_id, wavelet_id,
                   prop=blip_data)
    self.__context.AddOperation(op)
    return blip_data

  def WaveletAddParticipant(self, wave_id, wavelet_id, participant_id):
    """Requests to add a participant to a wavelet.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      participant_id: Id of the participant to add.
    """
    op = Operation(WAVELET_ADD_PARTICIPANT, wave_id, wavelet_id,
                   prop=participant_id)
    self.__context.AddOperation(op)

  def WaveletCreate(self, wave_id):
    """Requests to create a wavelet in a wave.

    Not yet implemented.

    Args:
      wave_id: The wave id owning that this operation is applied to.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def WaveletRemoveSelf(self, wave_id, wavelet_id):
    """Requests to remove this robot from a wavelet.

    Not yet implemented.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def WaveletSetDataDoc(self, wave_id, wavelet_id, name, data):
    """Requests set a key/value pair on the data document of a wavelet.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      name: The key name for this data.
      data: The value of the data to set.
    """
    op = Operation(WAVELET_DATADOC_SET, wave_id, wavelet_id,
                   blip_id=name, prop=data)
    self.__context.AddOperation(op)

  def WaveletSetTitle(self, wave_id, wavelet_id, title):
    """Requests to set the title of a wavelet.

    Not yet implemented.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      title: The title to set.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def BlipCreateChild(self, wave_id, wavelet_id, blip_id):
    """Requests to create a child blip of another blip.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.

    Returns:
      BlipData instance for which further operations can be applied.
    """
    blip_data = self.__CreateNewBlipData(wave_id, wavelet_id)
    op = Operation(BLIP_CREATE_CHILD, wave_id, wavelet_id,
                   blip_id=blip_id,
                   prop=blip_data)
    self.__context.AddOperation(op)
    return blip_data

  def BlipDelete(self, wave_id, wavelet_id, blip_id):
    """Requests to delete (tombstone) a blip.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
    """
    op = Operation(BLIP_DELETE, wave_id, wavelet_id, blip_id=blip_id)
    self.__context.AddOperation(op)

  def DocumentAnnotationDelete(self, wave_id, wavelet_id, blip_id, start, end,
                               name):
    """Deletes a specified annotation of a given range with a specific key.

    Not yet implemented.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      start: Start position of the range.
      end: End position of the range.
      name: Annotation key name to clear.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def DocumentAnnotationSet(self, wave_id, wavelet_id, blip_id, start, end,
                            name, value):
    """Set a specified annotation of a given range with a specific key.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      start: Start position of the range.
      end: End position of the range.
      name: Annotation key name to clear.
      value: The value of the annotation across this range.
    """
    annotation = document.Annotation(name, value, document.Range(start, end))
    op = Operation(DOCUMENT_ANNOTATION_SET, wave_id, wavelet_id,
                   blip_id=blip_id,
                   prop=annotation)
    self.__context.AddOperation(op)

  def DocumentAnnotationSetNoRange(self, wave_id, wavelet_id, blip_id,
                                   name, value):
    """Requests to set an annotation on an entire document.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      name: Annotation key name to clear.
      value: The value of the annotation.
    """
    annotation = document.Annotation(name, value, None)
    op = Operation(DOCUMENT_ANNOTATION_SET_NORANGE, wave_id, wavelet_id,
                   blip_id=blip_id,
                   prop=annotation)
    self.__context.AddOperation(op)

  def DocumentAppend(self, wave_id, wavelet_id, blip_id, content):
    """Requests to append content to a document.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      content: The content to append.
    """
    op = Operation(DOCUMENT_APPEND, wave_id, wavelet_id,
                   blip_id=blip_id,
                   prop=content)
    self.__context.AddOperation(op)

  def DocumentAppendStyledText(self, wave_id, wavelet_id, blip_id, text, style):
    """Requests to append styled text to the document.

    Not yet implemented.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      text: The text ot append..
      style: The style to apply.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def DocumentDelete(self, wave_id, wavelet_id, blip_id, start, end):
    """Requests to delete content in a given range.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      start: Start of the range.
      end: End of the range.
    """
    range = None
    if start != end:
      range = document.Range(start, end)
    op = Operation(DOCUMENT_DELETE, wave_id, wavelet_id, blip_id,
                   prop=range)
    self.__context.AddOperation(op)

  def DocumentInsert(self, wave_id, wavelet_id, blip_id, content, index=0):
    """Requests to insert content into a document at a specific location.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      content: The content to insert.
      index: The position insert the content at in ths document.
    """
    op = Operation(DOCUMENT_INSERT, wave_id, wavelet_id, blip_id,
                   index=index, prop=content)
    self.__context.AddOperation(op)

  def DocumentReplace(self, wave_id, wavelet_id, blip_id, content):
    """Requests to replace all content in a document.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      content: Content that will replace the current document.
    """
    op = Operation(DOCUMENT_REPLACE, wave_id, wavelet_id, blip_id,
                   prop=content)
    self.__context.AddOperation(op)

  def DocumentElementAppend(self, wave_id, wavelet_id, blip_id, element):
    """Requests to append an element to the document.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      element: Element instance to append.
    """
    op = Operation(DOCUMENT_ELEMENT_APPEND, wave_id, wavelet_id, blip_id,
                   prop=element)
    self.__context.AddOperation(op)

  def DocumentElementDelete(self, wave_id, wavelet_id, blip_id, position):
    """Requests to delete an element from the document at a specific position.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      position: Position of the element to delete.
    """
    op = Operation(DOCUMENT_ELEMENT_DELETE, wave_id, wavelet_id, blip_id,
                   index=position)
    self.__context.AddOperation(op)

  def DocumentElementInsert(self, wave_id, wavelet_id, blip_id, position,
                            element):
    """Requests to insert an element to the document at a specific position.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      position: Position of the element to delete.
      element: Element instance to insert.
    """
    op = Operation(DOCUMENT_ELEMENT_INSERT, wave_id, wavelet_id, blip_id,
                   index=position,
                   prop=element)
    self.__context.AddOperation(op)

  def DocumentElementInsertAfter(self):
    """Requests to insert an element after the specified location.

    Not yet implemented.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def DocumentElementInsertBefore(self):
    """Requests to insert an element before the specified location.

    Not yet implemented.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()

  def DocumentElementReplace(self, wave_id, wavelet_id, blip_id, position,
                             element):
    """Requests to replace an element.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      position: Position of the element to replace.
      element: Element instance to replace.
    """
    op = Operation(DOCUMENT_ELEMENT_REPLACE, wave_id, wavelet_id, blip_id,
                   index=position,
                   prop=element)
    self.__context.AddOperation(op)

  def DocumentInlineBlipAppend(self, wave_id, wavelet_id, blip_id):
    """Requests to create and append a new inline blip to another blip.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.

    Returns:
      A BlipData instance containing the id information.
    """
    inline_blip_data = self.__CreateNewBlipData(wave_id, wavelet_id)
    op = Operation(DOCUMENT_INLINE_BLIP_APPEND, wave_id, wavelet_id,
                   blip_id=blip_id,
                   prop=inline_blip_data)
    self.__context.AddOperation(op)
    inline_blip_data.parent_blip_id = blip_id
    return inline_blip_data

  def DocumentInlineBlipDelete(self, wave_id, wavelet_id, blip_id,
                               inline_blip_id):
    """Requests to delete an inline blip from its parent.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      inline_blip_id: The blip to be deleted.
    """
    op = Operation(DOCUMENT_INLINE_BLIP_DELETE, wave_id, wavelet_id,
                   blip_id=blip_id,
                   prop=inline_blip_id)
    self.__context.AddOperation(op)

  def DocumentInlineBlipInsert(self, wave_id, wavelet_id, blip_id, position):
    """Requests to insert an inline blip at a specific location.

    Args:
      wave_id: The wave id owning that this operation is applied to.
      wavelet_id: The wavelet id that this operation is applied to.
      blip_id: The blip id that this operation is applied to.
      position: The position in the document to insert the blip.

    Returns:
      BlipData for the blip that was created for further operations.
    """
    inline_blip_data = self.__CreateNewBlipData(wave_id, wavelet_id)
    inline_blip_data.parent_blip_id = blip_id
    op = Operation(DOCUMENT_INLINE_BLIP_INSERT, wave_id, wavelet_id,
                   blip_id=blip_id,
                   index=position,
                   prop=inline_blip_data)
    self.__context.AddOperation(op)
    return inline_blip_data

  def DocumentInlineBlipInsertAfterElement(self):
    """Requests to insert an inline blip after an element.

    Raises:
      NotImplementedError: Function not yet implemented.
    """
    raise NotImplementedError()
