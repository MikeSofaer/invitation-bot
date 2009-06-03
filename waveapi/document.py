#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc. All Rights Reserved.

"""Defines document-based classes.

This module defines classes that are used to modify and describe documents and
their operations.
"""

__author__ = 'davidbyttow@google.com (David Byttow)'

import util


class Range(object):
  """Represents a start and end range with integers.

  Ranges map positions in the document. A range must have at least a length
  of zero. If zero, the range is considered to be a single point (collapsed).
  """

  java_class = 'com.google.wave.api.Range'

  def __init__(self, start=0, end=1):
    """Initializes the range with a start and end position.

    Args:
      start: Start index of the range.
      end: End index of the range.

    Raises:
      ValueError: Value error if the range is invalid (less than zero).
    """
    self.start = start
    self.end = end
    if self.end - self.start < 0:
      raise ValueError('Range cannot be less than 0')

  def __str__(self):
    return 'Range(' + str(self.start) + ', ' + str(self.end) + ')'

  def IsCollapsed(self):
    """"Returns true if this represents a single point as opposed to a range."""
    return self.end == self.start


class Annotation(object):
  """Represents an annotation on a document.

  Annotations are key/value pairs over a range of content. Annotations
  can be used to store data or to be interpreted by a client when displaying
  the data.
  """

  java_class = 'com.google.wave.api.Annotation'

  def __init__(self, name, value, r=None):
    """Initializes this annotation with a name and value pair and a range.

    Args:
      name: Key name for this annotation.
      value: Value of this annotation.
      r: Range that this annotation is valid over.
    """
    self.name = name
    self.value = value
    self.range = r or Range()


class StringEnum(object):
  """Enum like class that is configured with a list of values.

  This class effectively implements an enum for Elements, except for that
  the actual values of the enums will be the string values."""

  def __init__(self, *values):
    for name in values:
      setattr(self, name, name)


ELEMENT_TYPE = StringEnum('INLINE_BLIP', 'INPUT', 'CHECK', 'LABEL', 'BUTTON',
    'RADIO_BUTTON', 'RADIO_BUTTON_GROUP','PASSWORD', 'GADGET', 'IMAGE')


class Element(object):
  """Elements are non-text content within a document.

  These are generally abstracted from the Robot. Although a Robot can query the
  properties of an element it can only interact with the specific types that
  the element represents.

  Properties of elements are both accesible directly (image.url) and through
  the properties dictionary (image.properties['url']). In general Element
  should not be instantiated by robots, but rather rely on the derrived classes.
  """

  java_class = 'com.google.wave.api.Element'

  def __init__(self, element_type, **properties):
    """Initializes self with the specified type and any properties."""
    self.type = element_type
    for key, val in properties.items():
      setattr(self, key, val)

  def Serialize(self):
    """Custom serializer for Elements.

    Element need their non standard attributes returned in a dict named
    properties.
    """
    props = {}
    data = {}
    for attr in dir(self):
      if attr.startswith('_'):
        continue
      val = getattr(self, attr)
      if val is None or callable(val):
        continue
      val = util.Serialize(val)
      if attr == 'type' or attr == 'java_class':
        data[attr] = val
      else:
        props[attr] = val
    data['properties'] = util.Serialize(props)
    return data


class FormElement(Element):

  java_class = 'com.google.wave.api.FormElement'

  def __init__(self, element_type, name, value='', default_value='', label=''):
    super(FormElement, self).__init__(element_type,
        name=name, value=value, default_value=default_value, label=label)


class Gadget(Element):

  java_class = 'com.google.wave.api.Gadget'

  def __init__(self, url=''):
    super(Gadget, self).__init__(ELEMENT_TYPE.GADGET, url=url)


class Image(Element):

  java_class = 'com.google.wave.api.Image'

  def __init__(self, url='', width=None, height=None,
      attachment_id=None, caption=None):
    super(Image, self).__init__(ELEMENT_TYPE.IMAGE, url=url, width=width,
        height=height, attachment_id=attachment_id, caption=caption)
