# Copyright (c) 2002 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.18 $
# Zope
from AccessControl import ModuleSecurityInfo
# Silva interfaces
from ISilvaObject import ISilvaObject
from IVersioning import IVersioning
from IContainer import IContainer
from IAsset import IAsset
# Silva 
import SilvaPermissions
# python
import string, re, urllib
from cgi import escape



module_security =  ModuleSecurityInfo('Products.Silva.helpers')

_id_re = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_\.-]*$')
p_ID = re.compile(r'^(.*?)([0-9]+)$')

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
    'code_source', 
    'content.html', 
    'edit',
    'form',
    'fulltext',
    'getBatch',
    'getDocmaFormatName',
    'globals',
    'index_html', 
    'layout_macro.html',
    'logout',
    'lookup',
    'memberform',
    'override.html', 
    'placeholder',
    'preview_html', 
    'promptWindow',
    'quotify',
    'redirect',
    'search',
    'standard_error_message', 
    'standard_unauthorized_message',
    'submit',
     )

module_security.declarePublic('escape_entities')
def escape_entities(text):
    """Escape entities.
    """
    return escape(text, 1)

module_security.declarePublic('IdCheckValues')
class IdCheckValues:
    """ actually only a record of values returned by the check_valid_id method """

    # hack to allow to access the values by python scripts
    # this does allow to write to there values ...
    __allow_access_to_unprotected_subobjects__ = 1

    ID_OK = 0
    ID_CONTAINS_BAD_CHARS = 1
    # id has a reserved prefix
    ID_RESERVED_PREFIX = 2
    # id is "used internally" which either means this id would 
    # shadowing some non-silva attribute, or is in the list of disallowed ids anyway
    ID_RESERVED = 3
    ID_IN_USE_CONTENT = 4
    ID_IN_USE_ASSET = 5
    


def getNewId(old_id):
    """returns an id based on the old id

        if old_id ends with a number, the number is increased, 
        otherwise 2 is appended
    """
    
    m = p_ID.match(old_id)
    if m is None: return '%s2' % (old_id, )
    
    name = m.group(1)
    count = int(m.group(2))
    
    return "%s%i" % (name, count+1)
    

_marker = ()

module_security.declarePublic('check_valid_id')
def check_valid_id(folder, maybe_id, allow_dup=0):
    """ test if the given id is valid, returning a status code
        about its validity or reason of invalidity
    """

    if _id_re.search(maybe_id) is None:
        return IdCheckValues.ID_CONTAINS_BAD_CHARS
    prefixing = maybe_id.split('_')
    if (len(prefixing)>1) and (prefixing[0] in _reserved_prefixes):
        return IdCheckValues.ID_RESERVED_PREFIX

    if maybe_id in _reserved_ids:
        return IdCheckValues.ID_RESERVED

    attr = getattr(folder.aq_inner, maybe_id, _marker)
    if attr is not _marker:
        if ISilvaObject.isImplementedBy(attr):
            # there is a silva object with the same id
            if allow_dup: return IdCheckValues.ID_OK
            attr = getattr(folder.aq_base, maybe_id, _marker)
            if attr is _marker:
                # shadowing a content object is ok (hopefully)
                return IdCheckValues.ID_OK
            if IAsset.isImplementedBy(attr):
                return IdCheckValues.ID_IN_USE_ASSET
            # else it must be a content object (?)
            return IdCheckValues.ID_IN_USE_CONTENT

        # check if object with this id is acquired; if not, it cannot be allowed
        attr2 = getattr(folder.aq_base, maybe_id, _marker)
	if attr2 is not _marker:
	    return IdCheckValues.ID_RESERVED

        # object using wanted id is acquried
        # now it may be a Zope object, which is allowed (for now)
        # or it is an attribute (which is disallowed)
        if not hasattr(attr, 'meta_type'):
            # not a zope object (guessing ...)            
            return IdCheckValues.ID_RESERVED
    
    return IdCheckValues.ID_OK


module_security.declarePublic('check_valid_id_file')
def check_valid_id_file(folder, id, file):
    """ special check for image, which may use the file name for id creation"""
    from OFS import Image
    from Products.Silva.File import TRANSMAP
    import string
    id, unused_title = Image.cookId(id, "", file)
    id = string.translate(id, TRANSMAP)
    return (id, check_valid_id(folder, id))
    

def add_and_edit(self, id, REQUEST):
    """Helper function to point to the object's management screen if
    'Add and Edit' button is pressed.
    id -- id of the object we just added
    """
    if REQUEST is None:
        return
    try:
        u = self.DestinationURL()
    except:
        u = REQUEST['URL1']
    if REQUEST.has_key('submit_edit'):
        u = "%s/%s" % (u, urllib.quote(id))
    REQUEST.RESPONSE.redirect(u+'/manage_main')

def unapprove_helper(object):
    """Unapprove object and anything unapprovable contained by it.
    """
    if IVersioning.isImplementedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
    if IContainer.isImplementedBy(object):
        for item in object.get_ordered_publishables():
            unapprove_helper(item)
    
def unapprove_close_helper(object):
    """Unapprove/close object and anything unapprovable/closeable contained by it.
    """
    if IVersioning.isImplementedBy(object):
        if object.is_version_approved():
            object.unapprove_version()
        if object.is_version_published():
            object.close_version()
    if IContainer.isImplementedBy(object):
        default = object.get_default()
        if default:
            unapprove_close_helper(default)
        for item in object.get_ordered_publishables():
            unapprove_close_helper(item)

# this is a bit of a hack; using implementation details of ParsedXML..
from Products.ParsedXML.PrettyPrinter import _translateCdata, _translateCdataAttr

translateCdata = _translateCdata
translateCdataAttr = _translateCdataAttr

#
# This code is not here to stay. It is an experimental "proof of concept"
# implementation for resticting view access on Silva objects based on
# ip addresses. We need a more generic approach integrated in the silva core
# e.g. based on roles?
#
# This code is based on Clemens Klein-Robbenhaar's "CommentParser.py" 
# Marc Petitmermet's and Wolfgang Korosec's code.
#
security = ModuleSecurityInfo('Products.Silva.helpers')
security.declarePublic('parseAccessRestriction')

__all__ = ('parseAccessRestriction',)

ACCESS_RESTRICTION_PROPERTY = 'access_restriction'

# match any quote _not_ preceeded by a backslash
quote_split = re.compile(r'(?<![^\\]\\)"', re.M)

# match any escapes of quotes (e.g. \\ or \" )
drop_escape = re.compile(r'\\(\\|")')

def parseAccessRestriction(item):
    raw_string = ''
    #if item.implements_container():
    # use "getattr" to get aquired access restrictions.
    raw_string = getattr(item, ACCESS_RESTRICTION_PROPERTY, '')
    #elif item.implements_versioned_content():
    #    raw_string = item.getProperty(DOCUMENT_PROPERTY, '')
    if not raw_string: return {}

    return _parse_raw(raw_string)

#stupid record
class State:
    pass

def _parse_raw(raw_string):
    props = {}

    state = State()
    
    # first split due to quotes
    quoted = quote_split.split(raw_string)

    in_quote = None
    state.read_props = None

    for item in quoted:
        if in_quote:
            _parse_quote(item, state, props)
        else:
            _parse_unquote(item, state, props)
            
        in_quote = not in_quote
    
    return props


def _parse_unquote(something, state, props):
    
    if not state.read_props:
        try:
            name, something = map (string.strip, something.split(':',1) )
        except ValueError:
            # no name: quit.
            return
        state.name = name
        props[name] = []
        state.plist = props[name]
        state.read_props = 1

    separate = something.split(';',1)
    if len(separate) > 1:
        something, rest = map (string.strip, separate)
    else:
        rest=None

    for p in map (string.strip, something.split(',') ):
        if p:
            state.plist.append(p)

    if rest is not None:
        state.read_props=None
        _parse_unquote(rest, state, props)


def _parse_quote(something, state, props):
    """ parse everything enclosed in quotes.
    this is an easy one: just remove the escapes
    """
    if not state.read_props:
        raise ValueError, "not inside a property definition: <<%s>>" % something

    something = drop_escape.sub(lambda match: match.group(1), something )
    state.plist.append(something)
    
