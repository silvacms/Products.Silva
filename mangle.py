# -*- coding: iso-8859-1 -*-
# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Python
import string
import re
import cgi
from types import StringType, UnicodeType

# Zope
from AccessControl import ModuleSecurityInfo
from DateTime import DateTime as _DateTime

# Silva
from interfaces import ISilvaObject, IAsset
from Products.Silva import characters

module_security = ModuleSecurityInfo('Products.Silva.mangle')

__allow_access_to_unprotected_subobjects__ = 1

def unquote(quoted):
    """A very simplified urllib2 unquote, only handles ?, = and &"""
    unquoted = quoted.replace(
        '%3D', '=').replace('%26', '&').replace('%3F', '?')
    return unquoted


class _Marker:
    """A marker"""
    
_marker = _Marker()

module_security.declarePublic('Id')
class Id:
    """silva id mangler

        usage:

            from Products.Silva import mangle
            if mangle.Id(myId).isValid():
                ...
            myId = mangle.Id(myId).new()
    """ 
    __allow_access_to_unprotected_subobjects__ = 1

    OK = 0
    CONTAINS_BAD_CHARS = 1
    # id has a reserved prefix
    RESERVED_PREFIX = 2
    # id is "used internally" which either means this id would 
    # shadowing some non-silva attribute, or is in the list of disallowed ids anyway
    RESERVED = 3
    IN_USE_CONTENT = 4
    IN_USE_ASSET = 5
    RESERVED_POSTFIX = 6
    IN_USE_ZOPE = 7
    
    
    # does only match strings containig valid chars
    _valid_id = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\.\-]*$')
    # finds postfixing number
    _number_postfix = re.compile(r'^(.*?)([0-9]+)$')
    
    # sequence of all reserved prefixes (before the first '_')
    _reserved_prefixes = (
        'aq',
        'get',
        'manage',
        'service',
        'set',
        )

    # all reserved/internally used ids. (This list is most probably incomplete)
    _reserved_ids = (
        'Members',
        'REQUEST',
        'acl_users',
        'cached',
        'cancel',
        'code_source',
        'content',
        'content.html',
        'delete',
        'edit',
        'email',
        'elements',
        'form',
        'fulltext',
        'getBatch',
        'getDocmaFormatName',
        'globals',
        'home',
        'index_html',
        'insert',
        'layout_macro.html',
        'logout',
        'lookup',
        'memberform',
        'override.html',
        'object_path',
        'path',
        'placeholder',
        'preview_html',
        'promptWindow',
        'quotify',
        'redirect',
        'render',
        'save',
        'standard_error_message',
        'standard_unauthorized_message',
        'submit',
        'up',
        'version_status'
         )

    _reserved_ids_for_interface = {
        IAsset: ('index', )
    }

    _validation_result = None

    def __init__(self, folder, maybe_id, allow_dup=0, file=None, instance=None,
            interface=None):
        """
            folder: container where the id should be valid
            maybe_id: the id (str) to be mangled
            allow_dup: if true an already existing id will be valid aswell
            file: file like object, allows to generate an id from it's filename
            instance: addtional tests for interfaces implemented by this 
                instance will be processed
            interface: an interface, additional tests regarding this interface
                will be processed
        """
        orig_id = maybe_id
        if type(maybe_id) == StringType:
            try:
                maybe_id = unicode(maybe_id, 'utf-8')
            except UnicodeError:
                maybe_id = unicode(maybe_id, 'latin-1', 'replace')
        if type(maybe_id) != UnicodeType:
            msg = "id must be str or unicode (%r)" % orig_id
            raise ValueError, msg
        if interface not in self._reserved_ids_for_interface.keys():
            interface = None
        self._folder = folder
        self._maybe_id = maybe_id
        self._allow_dup = allow_dup
        self._file = file
        self._instance = instance
        self._interface = interface

    def cook(self):
        """makes the id valid
        
            strips all not allowed characters from id, or if id is None uses
            file.filename for guessing a id

            returns self
        """
        from OFS import Image
        id, unused_title = Image.cookId(self._maybe_id, "", self._file)
        if type(id) == StringType:
            try:
                id = unicode(id, 'utf-8')
            except UnicodeError:
                pass
        if type(id) == UnicodeType:
            id = id.encode('latin1', 'replace')
        id = string.translate(id, characters.char_transmap)
        self._maybe_id = id
        self._validation_result = None
        return self

    def isValid(self):
        """returns true if id is valid, false otherwise"""
        return self.validate() == self.OK
       
    def validate(self):
        if self._validation_result is None:
            self._validation_result = self._validate()
        return self._validation_result
    
    def _validate(self):
        """ test if the given id is valid, returning a status code
            about its validity or reason of invalidity
        """
        folder = self._folder
        maybe_id = self._maybe_id
        allow_dup = self._allow_dup
        if self._valid_id.match(maybe_id) is None:
            return self.CONTAINS_BAD_CHARS
        if maybe_id.endswith('__'):
            # ugly, but Zope explicitely checks this ...
            return self.RESERVED_POSTFIX
        prefixing = maybe_id.split('_')
        if (len(prefixing)>1) and (prefixing[0] in self._reserved_prefixes):
            return self.RESERVED_PREFIX

        if maybe_id in self._reserved_ids:
            return self.RESERVED
        
        if self._instance is not None:
            for interface, prefixes in \
                    self._reserved_ids_for_interface.items():
                if interface.providedBy(self._instance):
                    if maybe_id in prefixes:
                        return self.RESERVED
        if self._interface is not None:
            if maybe_id in self._reserved_ids_for_interface[self._interface]:
                return self.RESERVED

        attr = getattr(folder.aq_inner, maybe_id, _marker)
        if attr is not _marker:
            if ISilvaObject.providedBy(attr):
                # there is a silva object with the same id
                if allow_dup: return self.OK
                attr = getattr(folder.aq_base, maybe_id, _marker)
                if attr is _marker:
                    # shadowing a content object is ok (hopefully)
                    return self.OK
                if IAsset.providedBy(attr):
                    return self.IN_USE_ASSET
                # else it must be a content object (?)
                return self.IN_USE_CONTENT

            # check if object with this id is acquired; if not, it cannot be 
            # allowed
            attr2 = getattr(folder.aq_base, maybe_id, _marker)
            if attr2 is not _marker:
                #either it is an attribute/method (self.RESERVED)
                #or it is an object within the container (self.IN_USE_ZOPE)
                if maybe_id in folder.objectIds():
                    return self.IN_USE_ZOPE
                else:
                    return self.RESERVED

            # object using wanted id is acquried
            # now it may be a Zope object, which is allowed (for now)
            # or it is an attribute (which is disallowed)
            if not hasattr(attr, 'meta_type'):
                # not a zope object (guessing ...)
                return self.RESERVED
        
        return self.OK

    def new(self):
        """changes id based on the old id to get a potentially unique id

            if old_id ends with a number, the number is increased, otherwise 2,
            3, 4, ... is appended until the id is available
            
            returns self
            raises ValueError if id is not valid
        """
        self._allow_dup = 1
        if not self.isValid():
            raise ValueError, "The id %r is not valid" % (self._maybe_id, )
        m = self._number_postfix.match(self._maybe_id)
        if m is None:
            new_id =  '%s2' % (self._maybe_id, )
        else:
            name = m.group(1)
            count = int(m.group(2))
            new_id = "%s%i" % (name, count+1)
        self._maybe_id = new_id
        self._validation_result = None
        return self

    def unique(self):
        """changes id to a unique one in current folder

            returns self
            raises ValueError if id is not valid
        """
        used_ids = self._folder.objectIds()
        while self._maybe_id in used_ids:
            self.new()
        return self
            
    def __str__(self):
        return self._maybe_id

class _Path:
    """mangle path
    
        i.e. /foo/bar, /foo/bar/baz -> baz
    
        SINGLETON
    """
    
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __call__(self, base_path, item_path):
        """mangle path"""
        i = 0
        absolute = 0
        for i in range(0, min(len(item_path), len(base_path))):
            if item_path[i] != base_path[i]:
                absolute = 1
                break
        if not absolute:
            item_path = item_path[len(base_path):]
        return item_path
    
    def fromObject(self, obj_context, obj):
        """return mangled path from object's context and object
        
            obj_context: str (path) or list
            obj: instance

            return str
        """
        if type(obj_context) == type(''):
            obj_context = obj_context.split('/')
        assert type(obj_context) in [list, tuple], \
                        "obj_context is not list type"
        obj_path = obj.getPhysicalPath()
        rel_path = '/'.join(self(obj_context, obj_path))
        if rel_path == '':
            # points to same object, to avoid problems we return an absolute
            # path
            return '/'.join(obj_path)
        return rel_path

    def toAbsolute(self, context_path, relative_path):
        """make a relative path absolute

            context_path: the path in which the relative path should be made
                absolute
            relative_path: the relative path to be made absolute
        """
        relative_path_in = relative_path
        context_path = self.strip(context_path)
        relative_path = self.strip(relative_path)
        if relative_path[0] == '':
            # path is absolute, starting with '/'
            return relative_path
        # strip "document part":
        del(context_path[-1])
        # handle "crawl up"
        while relative_path[0] == '..':
            del(relative_path[0])
            if not context_path:
                return relative_path_in
            del(context_path[-1])
        # concatenate paths
        abs_path = context_path + relative_path
        return abs_path

    def strip(self, path):
        """strip 'foo/./bar' to 'foo/bar'"""
        path = [ e for e in path if e != '.' ]
        return path
        
        

module_security.declarePublic('Path')
Path = _Path()
        

class _Entities:
    """escape entities"""
    
    def __call__(self, text):
        """return text with &, >, < and " escaped by their html entities"""
        return cgi.escape(text, 1)

module_security.declarePublic('entities')
entities = _Entities()

module_security.declarePublic('DateTime')
class DateTime:
    
    __allow_access_to_unprotected_subobjects__ = 1
    
    def __init__(self, dt):
        self._dt = dt
    
    def toStr(self):
        dt = self._dt
        if dt is None:
            return ''
        return "%02d %s %04d %02d:%02d" % (dt.day(), dt.aMonth().lower(),
            dt.year(), dt.hour(), dt.minute())
    __str__ = toStr

    def toDashedDateStr(self):
        dt = self._dt
        if dt is None:
            return ''
        return "%02d-%02d-%04d" % (dt.day(), dt.month(), dt.year())
    
    def toDateStr(self):
        dt = self._dt
        if dt is None:
            return ''
        return "%02d %s %s" % (dt.day(), dt.aMonth().lower(), dt.yy())
    
    def toShortStr(self):
        dt = self._dt
        if dt is None:
            return ''
        return "%02d&nbsp;%s&nbsp;%s&nbsp;%02d:%02d" % (dt.day(),
            dt.aMonth().lower(), dt.yy(), dt.hour(), dt.minute())

    def toDottedStr(self):
        dt = self._dt
        if dt is None:
            return ''
        return "%02d.%s.%s&middot;%02d:%02d" % (dt.day(), dt.aMonth().lower(),
            dt.yy(), dt.hour(), dt.minute())

    def toStrOptionalTime(self):
        """returns self.toStr() unless time is 00:00, then it returns
            a similar string without the time
        """
        dt = self._dt
        if dt is None:
            return ''
        if int(dt.hour() == 0) and int(dt.minute()) == 0:
            return '%02d %s %04d' % (dt.day(), dt.aMonth().lower(), dt.year())
        return self.toStr()

module_security.declarePublic('Now')
class Now(DateTime):

    def __init__(self):
        self._dt = _DateTime()

    
class _List:
    """list mangler"""

    __allow_access_to_unprotected_subobjects__ = 1
    
    def __call__(self, elements):
        if not elements:
            return ''
        if len(elements) == 1:
            return elements[0]
        return ', '.join(elements[:-1]) + ' and ' + elements[-1]

module_security.declarePublic('List')
List = _List()


class _Bytes:
    """convert size to a human readable format
    size: int, size of a file in bytes
    returns str, like '8.2M'
    """

    __allow_access_to_unprotected_subobjects__ = 1

    _magnitudes = ['', 'k', 'MB', 'GB', 'TB']
    _magnitudes.reverse()

    _threshold = 512

    def __call__(self, nrOfBytes):
        size = float(nrOfBytes)
        threshold = self._threshold
        magnitude = self._magnitudes[:]
        mag = magnitude.pop()

        while size > threshold and magnitude:
            size = size / 1024
            mag = magnitude.pop()

        if int(size) == size:
            return '%i %s' % (size, mag)
        return '%.1f %s' % (size, mag)

module_security.declarePublic('Bytes')
Bytes = _Bytes()

class _String:
    """ string manipulations and conversions
    """

    __allow_access_to_unprotected_subobjects__ = 1

    _default_encoding = 'utf-8'

    def inputConvert(self, text, preserve_whitespace=0):
        """Turn input to unicode. Assume it is UTF-8.
        """
        if not preserve_whitespace:
            text = ' '.join(text.split())
        return unicode(text, self._default_encoding)

    def reduceWhitespace(self, text):
        return ' '.join(text.split())

    def truncate(self, text, max_length):
        if len(text) < max_length:
            return text
        return '%s...' % text[:(max_length - 3)]
    
    def centeredTruncate(self, text, max_length):
        if len(text) < max_length:
            return text
        part_length = (max_length - 3) / 2
        return '%s...%s' % (text[:part_length], text[-part_length:])

module_security.declarePublic('String')
String = _String()

def generateAnchorName(s):
    """Generate a valid name for an anchor.

    Anchors only accept the following characters [A-Z a-z 0-9 -_:.]

    HTML 4 also requires the first character to be in [A-Z a-z].
    """
    # we do not really solve this now, so what we return is not
    # XHTML compliant at all, but we must return the string for
    # backwards compatibility (and XSLT compatibility, which doesn't
    # use this code path at all..)
    if isinstance(s, unicode):
        s = s.encode('UTF-8')
    new = ''
    for c in s:
        if c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_:.':
            new += c
        else:
            new += '_'
    return new

module_security.declarePublic('generateAnchorName')
