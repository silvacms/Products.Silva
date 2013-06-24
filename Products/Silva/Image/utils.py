# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from collections import namedtuple
import re

Point = namedtuple('Point', ('x', 'y'))

class Size(namedtuple('Size', ('width', 'height'))):
    __slots__ = ()
    __allow_access_to_unprotected_subobjects__ = True

    @classmethod
    def from_points(cls, p1, p2):
        return cls(abs(p1.x - p2.x), abs(p1.y - p2.y))

    @property
    def surface(self):
        return self.width * self.height

    def __lt__(self, other):
        return self.surface < other.surface

    def __lte__(self, other):
        return self.surface <= other.surface

    def __gt__(self, other):
        return self.surface > other.surface

    def __gte__(self, other):
        return self.surface >= other.surface


class Rect(object):
    _STR_RE = re.compile(r'^(?P<x1>[0-9]+)[Xx](?P<y1>[0-9]+)-(?P<x2>[0-9]+)[Xx](?P<y2>[0-9]+)')

    @classmethod
    def parse(cls, string):
        match = cls._STR_RE.match(string)
        if match:
            p1 = Point(int(match.group('x1')), int(match.group('y1')))
            p2 = Point(int(match.group('x2')), int(match.group('y2')))
            return cls.from_points(p1, p2)
        return None

    @classmethod
    def from_points(cls, p1, p2):
        lower_vertex = Point(min(p1.x, p2.x), min(p1.y, p2.y))
        higher_vertex = Point(max(p1.x, p2.x), max(p1.y, p2.y))
        return cls(lower_vertex, Size.from_points(lower_vertex, higher_vertex))

    def __init__(self, lower_edge, size):
        self.size = size
        self.lower_edge = lower_edge

    def __str__(self):
        higher_edge = self.higher_edge
        return "%dx%d-%dx%d" % (self.lower_edge.x, self.lower_edge.y,
                               higher_edge.x, higher_edge.y)

    @property
    def higher_edge(self):
        return Point(self.lower_edge.x + self.size.width,
                     self.lower_edge.y + self.size.height)


class Format(object):
    JPEG = 'JPEG'
    PNG = 'PNG'
    GIF = 'GIF'

# Resize format

class PercentResizeSpec(object):
    re_percentage = re.compile(r'^([0-9\.]+)\%$')

    @classmethod
    def parse(cls, string):
        match = cls.re_percentage.match(string)
        if match:
            try:
                return cls(float(match.group(1)))
            except (TypeError, ValueError):
                return None
        return None

    def __init__(self, percent):
        self.percent = percent

    def __eq__(self, other):
        if isinstance(other, PercentResizeSpec):
            return self.percent == other.percent
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_size(self, image):
        width, height = image.get_size()
        return Size(int(width * self.percent / 100),
                    int(height * self.percent / 100))


class WHResizeSpec(object):
    re_WidthXHeight = re.compile(r'^([0-9]+|\*)[Xx]([0-9\*]+|\*)$')

    @classmethod
    def parse(cls, string):
        match = cls.re_WidthXHeight.match(string)
        width, height = (0, 0)
        if match:
            width = match.group(1)
            if width != '*':
                width = int(width)
            height = match.group(2)
            if height != '*':
                height = int(height)
            if '*' == width == height:
                return None
            return cls(width, height)
        return None

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def __eq__(self, other):
        if isinstance(other, WHResizeSpec):
            return (self.width, self.height) == (other.width, other.height)
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_size(self, image):
        image_width, image_height = image.get_size()
        width, height = (self.width, self.height)
        if width == '*':
            width = (height * image_width) / image_height
        if height == '*':
            height = (width * image_height) / image_width
        return Size(width, height)
