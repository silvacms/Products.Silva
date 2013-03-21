# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import string
import re

from AccessControl import ModuleSecurityInfo
from Acquisition import aq_inner
from OFS.ObjectManager import checkValidId
from OFS.interfaces import IObjectManager
from five import grok
from zExceptions import BadRequest
from zope.interface import providedBy

from silva.translations import translate as _
from silva.core.interfaces import ISilvaObject, IAsset, IContainer, ContentError
from silva.core.interfaces import ISilvaNameChooser
from Products.Silva import characters

module_security = ModuleSecurityInfo('Products.Silva.mangle')
_marker = object()


class NameValidator(grok.Subscription):
    grok.implements(ISilvaNameChooser)
    grok.context(IContainer)
    grok.order(10)

    def __init__(self, context):
        self.context = context

    def checkName(self, identifier, content, file=None, interface=None):
        if content is not None:
            interface = providedBy(content)
        mangle = Id(self.context, identifier, file=file, interface=interface)
        error = mangle.verify()
        if error is not None:
            raise error
        return True

    def chooseName(self, identifier, content, file=None, interface=None):
        if content is not None:
            interface = providedBy(content)
        mangle = Id(self.context, identifier, file=file, interface=interface)
        mangle = mangle.cook()
        return str(mangle)


class SilvaNameChooserDispatcher(grok.Adapter):
    grok.context(IContainer)
    grok.implements(ISilvaNameChooser)

    def __init__(self, container):
        self.container = container
        self.subscribers = grok.queryOrderedSubscriptions(
            self.container, ISilvaNameChooser)

    def checkName(self, identifier, content, file=None, interface=None):
        for checker in self.subscribers:
            checker.checkName(
                identifier, content, file=file, interface=interface)
        return True

    def chooseName(self, identifier, content, file=None, interface=None):
        for chooser in self.subscribers:
            chosen = chooser.chooseName(
                identifier, content, file=file, interface=interface)
            if chosen is not None:
                identifier = chosen
        return identifier


class ZopeNameChooser(grok.Adapter):
    grok.context(IObjectManager)
    grok.implements(ISilvaNameChooser)

    def __init__(self, container):
        self.container = container

    def checkName(self, identifier, content, file=None, interface=None):
        try:
            checkValidId(self.container, str(identifier))
        except BadRequest as error:
            raise ContentError(error.args[0], self.container)
        return True

    def chooseName(self, name, content, file=None, interface=None):
        return str(name)


module_security.declarePublic('Id')
class Id(object):
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
    # shadowing some non-silva attribute, or is in the list of
    # disallowed ids anyway
    RESERVED = 3
    IN_USE_CONTENT = 4
    IN_USE_ASSET = 5
    RESERVED_POSTFIX = 6
    IN_USE_ZOPE = 7
    RESERVED_FOR_CONTENT = 8

    # does only match strings containig valid chars
    _valid_id = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\.\-]*$')
    # finds postfixing number
    _number_postfix = re.compile(r'^(.*?)([0-9]+)$')

    # sequence of all reserved prefixes (before the first '_')
    _reserved_prefixes = (
        'cb',
        'aq',
        'get',
        'manage',
        'service',
        'set',
        )

    # all reserved/internally used ids. (This list is most probably
    # incomplete)
    _reserved_ids = set([
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
        'elements',
        'email',
        'form',
        'fulltext',
        'home',
        'index_html',
        'insert',
        'keys',
        'layout_macro.html',
        'logout',
        'lookup',
        'memberform',
        'object_path',
        'override.html',
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
        'values',
        'version_status'
         ])

    _reserved_ids_for_interface = {
        IAsset: ('index', ),
        IContainer: ('index', )
    }

    _validation_result = None

    def __init__(self, context, maybe_id, allow_dup=0, file=None, interface=None):
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
        if maybe_id is None:
            maybe_id = ""
        if isinstance(maybe_id, str):
            try:
                maybe_id = unicode(maybe_id, 'utf-8')
            except UnicodeError:
                maybe_id = unicode(maybe_id, 'latin-1', 'replace')
        if not isinstance(maybe_id, unicode):
            raise ValueError("id must be str or unicode (%r)" % orig_id)
        self._context = context
        self._maybe_id = maybe_id
        self._allow_dup = allow_dup
        self._file = file
        self._interface = interface

    def cook(self):
        """makes the id valid

            strips all not allowed characters from id, or if id is None uses
            file.filename for guessing a id

            returns self
        """
        from OFS import Image
        id, unused_title = Image.cookId(self._maybe_id, "", self._file)
        if isinstance(id, str):
            try:
                id = unicode(id, 'utf-8')
            except UnicodeError:
                pass
        if isinstance(id, unicode):
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

    def verify(self):
        status = self.validate()
        if status != self.OK:
            return ContentError(self._status_to_string(status), self._context)
        return None

    def _validate(self):
        """ test if the given id is valid, returning a status code
            about its validity or reason of invalidity
        """
        folder = self._context
        maybe_id = self._maybe_id
        allow_dup = self._allow_dup
        if self._valid_id.match(maybe_id) is None:
            return self.CONTAINS_BAD_CHARS
        if maybe_id.endswith('__'):
            # ugly, but Zope explicitely checks this ...
            return self.RESERVED_POSTFIX
        prefixing = maybe_id.split('_')
        if (len(prefixing) >1) and (prefixing[0] in self._reserved_prefixes):
            return self.RESERVED_PREFIX

        if maybe_id in self._reserved_ids:
            return self.RESERVED

        if self._interface is not None:
            for interface, prefixes in \
                    self._reserved_ids_for_interface.items():
                if self._interface.isOrExtends(interface):
                    if maybe_id in prefixes:
                        return self.RESERVED_FOR_CONTENT

        attr = getattr(aq_inner(folder), maybe_id, _marker)
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
        try:
            # Call Zope verification function
            checkValidId(folder, str(maybe_id), allow_dup)
        except BadRequest:
            return self.CONTAINS_BAD_CHARS

        return self.OK

    def _status_to_string(self, status):
        if status == self.CONTAINS_BAD_CHARS:
            return _(u'The id contains strange characters. It should only '
                     u'contain letters, digits and ‘_’ or ‘-’ or ‘.’ '
                     u'Spaces are not allowed and the id should start '
                     u'with a letter or digit.')
        elif status == self.RESERVED_PREFIX:
            prefix = str(self._maybe_id).split('_')[0]+'_'
            return _(u"ids starting with ${prefix} are reserved for "
                     u"internal use.",
                     mapping={'prefix': prefix})
        elif status == self.RESERVED:
            return _(u"The id ${id} is reserved for internal use.",
                     mapping={'id': self._maybe_id})
        elif status == self.IN_USE_CONTENT:
            return _(u"There is already an object with the id ${id} in this "
                     u"container.",
                     mapping={'id': self._maybe_id})
        elif status == self.IN_USE_ASSET:
            return _(u"There is already an asset with the id ${id} in this "
                     u"container.", mapping={'id': self._maybe_id})
        elif status == self.RESERVED_POSTFIX:
            return _(u"The id ${id} ends with invalid characters.",
                     mapping={'id': self._maybe_id})
        elif status == self.IN_USE_ZOPE:
            return _(u"The id ${id} is already in use by a Zope object.",
                     mapping={'id': self._maybe_id})
        elif status == self.RESERVED_FOR_CONTENT:
            return _("The id ${id} cannot be used for a content of this "
                     u"type.", mapping={'id': self._maybe_id})
        return _(u"(Internal Error): An invalid status ${status_code} occured "
                 u"while checking the id ${id}.",
                 mapping={'status_code': status, 'id': self._maybe_id})

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
        used_ids = self._context.objectIds()
        while self._maybe_id in used_ids:
            self.new()
        return self

    def __str__(self):
        return self._maybe_id


class _Bytes(object):
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
