from __future__ import nested_scopes

# python imports
import string
import re
from types import TupleType, ListType

# zope imports
import zLOG

# silva imports
from Products.Silva.interfaces import \
    ISilvaObject, IContainer, IVersionedContent, IVersion, IUpgrader
from Products.Silva.Membership import NoneMember, noneMember
from Products.Silva import mangle



class GeneralUpgrader:
    """wrapper for upgrade functions"""
    
    __implements__ = IUpgrader

    def __init__(self, upgrade_handler):
        """constructor

            upgrade_handler: function which actually does the upgrade
                one argument: the object to be opgraded
        """
        self._upgrade_handler = upgrade_handler

    def upgrade(self, obj):
        new_object = self._upgrade_handler(obj)
        if new_object:
            return new_obj
        return obj
   
    def __repr__(self):
        return "<GeneralUpgrader %r>" % self._upgrade_handler


# marker for upgraders to be called for any object
class AnyMetaType:
    pass
AnyMetaType = AnyMetaType()


class UpgradeRegistry:
    """Here people can register upgrade methods for their objects
    """
    
    def __init__(self):
        self.__registry = {}
        self._setUp = {}
        self._tearDown = {}
    
    def register(self, meta_type, upgrade_handler, version):
        """Register a meta_type for upgrade.

        The upgrade handler is called with the object as its only argument
        when the upgrade script encounters an object of the specified
        meta_type.
        """
        self.registerFunction(upgrade_handler, version, meta_type)

    def registerFunction(self, function, version, meta_type):
        upgrader = GeneralUpgrader(function)
        self.registerUpgrader(upgrader, version, meta_type)
        

    def registerUpgrader(self, upgrader, version, meta_type):
        assert IUpgrader.isImplementedBy(upgrader)
        self.__registry.setdefault(version, {}).setdefault(meta_type, []).\
            append(upgrader)

    def registerSetUp(self, function, version):
        self._setUp.setdefault(version, []).append(function)

    def registerTearDown(self, function, version):
        self._tearDown.setdefault(version, []).append(function)
        
    def getUpgraders(self, version, meta_type):
        """Return the registered upgrade_handlers of meta_type
        """
        upgraders = []
        v_mt = self.__registry.get(version, {})
        upgraders.extend(v_mt.get(meta_type, []))
        upgraders.extend(v_mt.get(AnyMetaType, []))
        return upgraders

    def upgradeObject(self, obj, version):
        mt = obj.meta_type
        for upgrader in self.getUpgraders(version, mt):
            zLOG.LOG('Silva', zLOG.INFO, 'Upgrading %s' % obj.absolute_url(),
                'Upgrading with %r' % upgrader)
            # sometimes upgrade methods will replace objects, if so the
            # new object should be returned so that can be used for the rest
            # of the upgrade chain instead of the old (probably deleted) one
            obj = upgrader.upgrade(obj)
        return obj
        
    def upgradeTree(self, root, version):
        """upgrade a whole tree to version"""
        metatype_upgrader_mapping = self.__registry.get(version)
        if not metatype_upgrader_mapping:
            # XXX: log something
            return
        
        self.setUp(root, version)
        object_list = [root]
        try:
            while object_list:
                o = object_list[0]
                del object_list[0]
                self.upgradeObject(o, version)
                if hasattr(o, 'objectValues'):
                    object_list.extend(o.objectValues())
        finally:
            self.tearDown(root, version)

    def upgrade(self, root, from_version, to_version):
        versions = self.__registry.keys()
        versions.sort(lambda x, y: cmp(self._vers_str_to_int(x),
            self._vers_str_to_int(y)))
        try:
            version_index = versions.index(from_version) + 1
        except ValueError:
            version_index = 0
        for version_index in range(version_index, len(versions)):
            self.upgradeTree(root, versions[version_index])

        
    def setUp(self, root, version):
        for function in self._setUp.get(version, []):
            function(root)
    
    def tearDown(self, root, version):
        for function in self._tearDown.get(version, []):
            function(root)

    def _vers_str_to_int(self, version):
        return tuple([ int(s) for s in version.split('.') ])

    def _vers_int_to_str(self, version):
        return '.'.join([ str(i) for i in version ])
        


upgrade_registry = UpgradeRegistry()
def check_reserved_ids(obj):
    """Walk through the entire tree to find objects of which the id is not
    allowed, and return a list of the urls of those objects
    """
    object_list = obj.objectValues()
    while object_list:
        o = object_list[0]
        del object_list[0]
        if IContainer.isImplementedBy(o):
            object_list.extend(o.objectValues())
        if not ISilvaObject.isImplementedBy(o):
            continue
        old_id = o.getId()
        id = mangle.Id(o.aq_parent, old_id, allow_dup=1)
        if id.isValid():
            continue
        id.cook()
        while not id.isValid():
            id = mangle.Id(o.aq_parent, 'renamed_%s' % id, allow_dup=0)
            o.aq_prent.manage_renameObject(old_id, str(id))
            zLOG.LOG("Silva", zLOG.INFO,
                'Invalid id %s found. Renamed to %s' % (old_id, str(id)),
                'Location: %s' % o.absolute_url())
upgrade_registry.registerFunction(check_reserved_ids, '0.9.2', AnyMetaType)
upgrade_registry.registerFunction(check_reserved_ids, '0.9.3', AnyMetaType)



#-----------------------------------------------------------------------------
# 0.9.1 to 0.9.2
#-----------------------------------------------------------------------------

# This is a complicated set of upgrades!! The order of the upgrades is important
# (they are called in the order in which they are registered), because most
# methods expect objects to be a certain type and the type can change somewhere
# in the chain of methods (old-style ParsedXML versions are converted to Version
# objects, which means that the way to perform certain actions on them changes)



def silvaDocumentBeforeDeleteDisable(root):
    # the manage_beforeDelete of the original Document doesn't work, since the 
    # code will look for a 'content' attribute, which doesn't yet exist on 
    # them, therefore we're going to have to do some trickery here...
    # This is a nasty piece of monkeypatching, mainly because other functionality
    # might require the original use of manage_beforeDelete somewhere, and
    # it isn't possible to monkeypatch the object since no reference to the object
    # can be used in monkeypatched object methods (self is not passed as a variable to
    # those methods)
    from Products.SilvaDocument.Document import Document
    upgrade_registry.old_manage_beforeDelete = Document.manage_beforeDelete
    def manage_beforeDelete_old_style_docs(self, item, container):
        Document.inheritedAttribute('manage_beforeDelete')(self, item,
            container)
    Document.manage_beforeDelete = manage_beforeDelete_old_style_docs
upgrade_registry.registerSetUp(silvaDocumentBeforeDeleteDisable, '0.9.2')

def silvaDocumentBeforeDeleteEnable(root):
    from Products.SilvaDocument.Document import Document
    Document.manage_beforeDelete = upgrade_registry.old_manage_beforeDelete
    delattr(upgrade_registry, 'old_manage_beforeDelete')
upgrade_registry.registerTearDown(silvaDocumentBeforeDeleteEnable, '0.9.2')

def root_092(root):
    # set the '_allow_authentication_requests' attribute on servce_members if
    # it isn't there yet
    sm = getattr(root, 'service_members', None)
    if sm is not None:
        if hasattr(sm, '_allow_subscription'):
            sm._allow_authentication_requests = sm._allow_subscription
            del sm._allow_subscription
        elif not hasattr(sm, '_allow_authentication_requests'):
            sm._allow_authentication_requests = 0
upgrade_registry.registerFunction(root_092, '0.9.2', 'Silva Root')


def upgrade_list_titles_in_parsed_xml(top):
    for child in top.childNodes:
        if child.nodeName in ('list', 'nlist', 'dlist'):
            for list_child in child.childNodes:
                if list_child.nodeType == list_child.TEXT_NODE:
                    continue
                if list_child.nodeName == 'title':
                    data = ''
                    for data_child in list_child.childNodes:
                        data += data_child.data
                    list_child.parentNode.removeChild(list_child)
                    if data.strip() == '':
                        break
                    heading = list_child.ownerDocument.createElement(
                        u'heading')
                    heading_text = list_child.ownerDocument.createTextNode(
                        data)
                    heading.appendChild(heading_text)
                    heading.setAttribute(u'type', u'subsub')
                    child.parentNode.insertBefore(heading, child)
                    break
                elif list_child.nodeName != 'title':
                    break
        if child.nodeName == 'nlist':
            for list_child in child.childNodes:
                if list_child.nodeType == list_child.TEXT_NODE:
                    continue
                upgrade_list_titles_in_parsed_xml(list_child)
        if child.nodeName == 'image':
            if child.hasAttribute('image_path'):
                path = child.getAttribute('image_path')
                newpath = path
                try:
                    image = top.restrictedTraverse(path.split('/'))
                    newpath = '/'.join(image.getPhysicalPath())
                except:
                    if path[0] == '/':
                        try:
                            image = top.restrictedTraverse(path[1:].split('/'))
                            newpath = '/'.join(image.getPhysicalPath())
                        except:
                            newpath = path 
                child.removeAttribute('image_path')
                if child.hasAttribute('image_id'):
                     child.removeAttribute('image_id')
                child.setAttribute('path', newpath)
            elif child.hasAttribute('image_id'):
                id = child.getAttribute('image_id')
                # XXX somehow, this way the image is not found...
                image = getattr(top.get_container(), id, None)
                newpath = id
                if image:
                    newpath = unicode('/'.join(image.getPhysicalPath()))
                child.removeAttribute('image_id')
                child.setAttribute('path', newpath)
        if child.nodeName == 'table':
            for table_child in child.childNodes:
                if table_child.nodeType == table_child.TEXT_NODE:
                    continue
                if table_child.nodeName != 'row':
                    continue
                for field in table_child.childNodes:
                    if field.nodeType == field.TEXT_NODE:
                        continue
                    upgrade_list_titles_in_parsed_xml(field)
        

from StringIO import StringIO

# small helper function to get the xml from an old-style version
def get_version_xml(obj, version):
    v = getattr(obj, version, None)
    if v is None:
        raise Exception, 'No version %s!' % version
    s = StringIO()
    v.documentElement.writeStream(s)
    return s.getvalue().encode('UTF8')

from Products.SilvaDocument.Document import DocumentVersion

def convert_document_092(obj):
    #print 'Converting document',  obj.id
    from random import randrange
    from string import lowercase
    from DateTime import DateTime

    for version in ['unapproved', 'approved', 'public', 'last_closed']:
        v = getattr(obj, 'get_%s_version' % version)()
        if v is not None and not hasattr(getattr(obj, v).aq_base, 'documentElement'):
            # bypass this document, as upgrade seems to be done already
            return

    def upgrade_doc_version(doc, version):
        xml = get_version_xml(doc, version)
        newver = DocumentVersion(version, doc._title)
        newver.content.manage_edit(xml)
        setattr(doc, version, newver)
        doc._update_publication_status()
            
    for version in ['unapproved', 'approved', 'public']:
        v = getattr(obj, 'get_%s_version' % version)()
        if v is not None:
            upgrade_doc_version(obj, v)

    if obj._previous_versions is not None:
        # the last element of previous versions is last_closed,
        # so that's done already
        # Make sure the versions all exist, users sometimes tend
        # to delete versions manually from the ZMI, since there's no
        # way to do that from the SMI, which corrupts the previous versions 
        # list
        new_previous_versions = []
        for versionid, pdt, edt in obj._previous_versions:
            if not hasattr(obj, versionid):
                continue
            upgrade_doc_version(obj, versionid)
            new_previous_versions.append((versionid, pdt, edt))
        obj._previous_versions = new_previous_versions
            
upgrade_registry.register('Silva Document', convert_document_092, '0.9.2')

# converting the data of the object to unicode will mostly (if not only)
# consist of converting metadata fields, so it is probably nice to do
# both in one go

# mapping from metadata set name to a mapping of old metadata field names to 
# new (the second mapping can not be the other way round since there can be several 
# old names for one new metadata field)
# the old names can refer to a Zope Property, an attribute or a method on the object
# note that this mapping is used to find out the fields that should be
# converted, so all to-be-converted fields should be mentioned
set_el_name_mapping = {
    'silva-content': {},
    'silva-extra': {
        'document_comment': 'comment', 
        'container_comment': 'comment',
        'subject': 'subject',
        'contact_email': 'contactemail',
        'contact_name': 'contactname',
        }
    }

# some helper function
def get_versions_or_self(obj):
    #print 'Getting versions of', obj.id
    ret = []
    if IVersionedContent.isImplementedBy(obj):
        versions = []
        for version in ['_unapproved_version', '_approved_version',
                        '_public_version']:
            v = getattr(obj, version)
            if v[0] is not None:
                versions.append(v)
            #print version, ':', v
        if obj._previous_versions is not None:
            versions += obj._previous_versions
            #print 'Previous versions:', obj._previous_versions
        for version in versions:
            #print 'Going to get version', version
            #print getattr(obj, version[0])
            ret.append(getattr(obj, version[0]))
    else:
        ret = [obj]
    return ret

def getPropertyOrAttrValue(object, attr):
    value = None
    if object.hasProperty(attr):
        value = object.getProperty(attr)
        object.manage_delProperties(ids=[attr])
    elif hasattr(object.aq_inner, attr):
        value = getattr(object.aq_inner, attr)
        # if it is not a string, skip it (e.g. when a folder we're
        # upgrading has content with an id which is also a name in 
        # the old style metadata.
        if type(value) != type(u'') or type(value) != type(''):
            return None
        #if callable(value):
        #    value = value()
        delattr(object.aq_inner, attr)
    return value

def unicode_and_metadata_092(obj):
    # get the metadata sets for the object
    ms = obj.service_metadata

    values = {}
    for set_name, el_name_mapping in set_el_name_mapping.items():
        for old_name, new_name in el_name_mapping.items():
            #print 'Testing for', old_name, 'on object', obj.absolute_url()
            old_value = getPropertyOrAttrValue(obj, old_name)
            if old_value is None:
                #print 'Not found'
                continue
            #print 'Old value:', old_value
            # if somehow the string is already unicode (who knows, right :)
            # skip conversion
            new_value = old_value
            if type(old_value) != type(u''):
                # we are assuming all data is cp1252 here, since that's what we've
                # been using all along, but maybe some funky custom setups may want
                # to interfere here...
                # XXX do we really want to continue on errors here instead of an exception?
                new_value = unicode(old_value, 'cp1252', 'replace')
            values[new_name] = new_value
        # now set it
        # if an object is a VersionedContent, walk through all versions, else just
        # set it to the current version
        objects = get_versions_or_self(obj)
        for object in objects:
            binding = ms.getMetadata(object)
            if binding is None:
                #print 'Binding object:', object.meta_type
                continue
            if set_name in binding.getSetNames():
                binding._setData(values, set_id=set_name, reindex=0)
                #print 'Values', str(values).encode('ascii', 'replace'), 'set on', obj.absolute_url()

upgrade_registry.register('Silva Root', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva Folder', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva Publication', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva Document', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva DemoObject', unicode_and_metadata_092, '0.9.2')
# FIXME: upgrade metadata for Ghosts and Assets? The title?
#upgrade_registry.register('Silva Ghost', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva Image', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva File', unicode_and_metadata_092, '0.9.2')
upgrade_registry.register('Silva SQL Data Source', unicode_and_metadata_092, '0.9.2')

            
def set_cache_data_092(obj):
    """ add the new cache data variable """
    # XXX does not check if content is already upgraded
    obj.cleanPublicRenderingCache()

upgrade_registry.register('Silva Document', set_cache_data_092, '0.9.2')
upgrade_registry.register('Silva Ghost', set_cache_data_092, '0.9.2')
upgrade_registry.register('Silva DemoObject', set_cache_data_092, '0.9.2')

def add_default_doc_092(obj):
    if not hasattr(obj, '_title'):
        # is new style folder, no title anymore
        return
    if obj.get_default() is None:
        obj.manage_addProduct['Silva'].manage_addDocument('index', obj._title)
        
upgrade_registry.register('Silva Folder', add_default_doc_092, '0.9.2')
upgrade_registry.register('Silva Publication', add_default_doc_092, '0.9.2')
upgrade_registry.register('Silva Root', add_default_doc_092, '0.9.2')

def replace_container_title_092(obj):
    """Move the title to the metadata
    
    Is a bit of a hairball situation, since the
    title should be set on all the versions
    of the default document, if one of those is
    available. If not, the title should just be
    removed
    """
    #print 'Replace container'
    if not '_title' in obj.aq_inner.__dict__.keys():
        return
    title = obj._title
    del obj._title
    if type(title) != type(u''):
        title = unicode(title, 'cp1252', 'replace')
    short_title = getPropertyOrAttrValue(obj, 'short_title')
    default = obj.get_default()
    if default is not None:
        #print 'Setting title', title.encode('ascii', 'replace'), 'on default of', obj.id
        # because this code is called *before* the folder is traversed,
        # the versionedcontent objects are still old style here, so we don't
        # have to go through all kinds of trouble to get all the versions
        # for those kind of objects
        default._title = title
    else:
        obj.manage_addProduct['Silva'].manage_addDocument('index', title)
        default = obj.index
    if short_title is not None:
        # set it to the default for now, the replace_object_title method
        # will pick it up then
        default.short_title = short_title

def replace_object_title_092(obj):
    """Move the title to the metadata
    """
    # get the metadata sets for the object
    ms = obj.service_metadata

    #print 'Replace object title for', obj.id
    if not '_title' in obj.aq_base.__dict__.keys():
        #print 'No title available on', obj.absolute_url()
        return
    #print obj.absolute_url()
    title = obj.aq_inner._title
    short_title = getPropertyOrAttrValue(obj, 'short_title')
    if short_title is not None and type(short_title) != type(u''):
        short_title = unicode(short_title, 'cp1252', 'replace')
    #print 'Title:', title.encode('ascii', 'replace')
    #print 'Plain title attribute:', obj.aq_inner.title
    #print dir(obj.aq_inner)
    #print obj.aq_base.__dict__
    del obj.aq_inner._title
    if type(title) != type(u''):
        title = unicode(title, 'cp1252', 'replace')
    objects = get_versions_or_self(obj)
    for object in objects:
        binding = ms.getMetadata(object)
        if object.get_title():
            continue
        #print 'Going to replace title of version', object.getPhysicalPath()
        #print 'New title:', title.encode('ascii', 'replace')
        object.set_title(title)
        #print type(title)
        #print type(object.title)
        
        if short_title is not None:
            set_name = 'silva-content'
            values = {'shorttitle': short_title}
            if binding is None:
                #print 'Binding object:', object.meta_type
                continue
            if set_name in binding.getSetNames():
                binding._setData(values, set_id=set_name, reindex=0)

upgrade_registry.register('Silva Root', replace_container_title_092, '0.9.2')
upgrade_registry.register('Silva Publication', replace_container_title_092, '0.9.2')
upgrade_registry.register('Silva Folder', replace_container_title_092, '0.9.2')
upgrade_registry.register('Silva Document', replace_object_title_092, '0.9.2')
upgrade_registry.register('Silva DemoObject', replace_object_title_092, '0.9.2')
upgrade_registry.register('Silva File', replace_object_title_092, '0.9.2')
upgrade_registry.register('Silva Image', replace_object_title_092, '0.9.2')
upgrade_registry.register('Silva SQL Data Source', replace_object_title_092, '0.9.2')
upgrade_registry.register('Silva Indexer', replace_object_title_092, '0.9.2')

def catalog_092(obj):
    obj.index_object()
    
def catalog_version_092(obj):
    """Do initial catalogin of objects"""
    #if not ICatalogedVersion.isImplementedBy(obj):
    #    return
    if obj.version_status() in ['last_closed', 'closed']:
        return
    obj.index_object()
    
upgrade_registry.register('Silva Root',
                          catalog_092, '0.9.2')
upgrade_registry.register('Silva Folder',
                          catalog_092, '0.9.2')
upgrade_registry.register('Silva Publication',
                          catalog_092, '0.9.2')
upgrade_registry.register('Silva Document Version',
                          catalog_version_092, '0.9.2')
upgrade_registry.register('Silva DemoObject Version',
                          catalog_version_092, '0.9.2')
upgrade_registry.register('Silva Ghost Version',
                          catalog_version_092, '0.9.2')

# helper methods for no-bullet list conversion
def get_text_from_node(node):
    nodelist = []
    for child in node.childNodes:
        if child.nodeType == 3 or child.nodeType == 6:
            nodelist.append(child)
    return nodelist

def replace_list(node):
    for child in node.childNodes:
        if child.nodeName == u'list' and child.getAttribute('type') == u'none':
            #print 'No bulleted lists'
            p = child.createElement('p')
            for sc in child.childNodes:
                if sc.nodeName == 'li':
                    textnodes = get_text_from_node(sc)
                    for textnode in textnodes:
                        p.appendChild(textnode)
                    breaknode = child.createElement('br')
                    p.appendChild(breaknode)
            node.replaceChild(p, child)
        elif child.hasChildNodes():
            replace_list(child)

def convert_no_bullet_lists_092(obj):
    topnode = obj.content.documentElement
    replace_list(topnode)

upgrade_registry.register('Silva Document Version', convert_no_bullet_lists_092, '0.9.2')
upgrade_registry.register('Silva DemoObject Version', convert_no_bullet_lists_092, '0.9.2')

def update_indexers_092(obj):
    obj.update_index()

upgrade_registry.register('Silva Indexer', update_indexers_092, '0.9.2')

#-----------------------------------------------------------------------------
# 0.9.2 to 0.9.3
#-----------------------------------------------------------------------------


class UpgradeAccessRestriction:
    """upgrade access restrction

        access restriction by ip address was a proof of concept and has been
        replaced by IP groups.

        This upgrade does:

            XXX

    """

    __implements__ = IUpgrader

    ACCESS_RESTRICTION_PROPERTY = 'access_restriction'

    # match any quote _not_ preceeded by a backslash
    re_quote_split = re.compile(r'(?<![^\\]\\)"', re.M)

    # match any escapes of quotes (e.g. \\ or \" )
    re_drop_escape = re.compile(r'\\(\\|")')


    def upgrade(self, obj):
        if not hasattr(obj.aq_base, '_properties'):
            # if it is not a property manager it hardly can have access 
            # restrictions
            return obj
        ar = self.parseAccessRestriction(obj).get('allowed_ip_addresses')
        if ar:
            ar = [ s.upper() for s in ar ]
            if 'ALL' in ar:
                self._all_allowed(obj)
            else:
                self._restrict(obj, ar)
        try:
            obj._delProperty(self.ACCESS_RESTRICTION_PROPERTY)
        except ValueError:
            pass
        return obj
        
    def _all_allowed(self, obj):
        pass

    def _restrict(self, obj, ar):
        if not obj.sec_is_closed_to_public():
            obj.sec_close_to_public()
        ipg = self._createIPGroup(obj)
        for ip in ar:
            ipg.addIPRange(ip)
        
    def _createIPGroup(self, context):
        if not IContainer.isImplementedBy(context):
            context = context.aq_parent
        assert IContainer.isImplementedBy(context)
        id = 'access_restriction_upgrade_group'
        id_template = id + '_%i'
        counter = 0
        while 1:
            if counter:
                id = id_template % counter
            try: 
                context.manage_addProduct['Silva'].manage_addIPGroup(id,
                    'Automatically created IP Group', id)
            except ValueError:
                counter += 1
            else:
                break
        return context._getOb(id)
    
    ### ACCCESS RESTRICTION PARSER
    ### formerly found in helpers.py

    # This code is based on Clemens Klein-Robbenhaar's "CommentParser.py" 
    # Marc Petitmermet's and Wolfgang Korosec's code.
    #
    def parseAccessRestriction(self, obj):
        raw_string = ''
        raw_string = getattr(obj.aq_base, self.ACCESS_RESTRICTION_PROPERTY, '')
        if not raw_string:
            return {}
        return self._parse_raw(raw_string)

    #stupid record
    class State:
        pass

    def _parse_raw(self, raw_string):
        props = {}
        state = self.State()
        # first split due to quotes
        quoted = self.re_quote_split.split(raw_string)
        in_quote = None
        state.read_props = None
        for item in quoted:
            if in_quote:
                self._parse_quote(item, state, props)
            else:
                self._parse_unquote(item, state, props)
            in_quote = not in_quote
        return props


    def _parse_unquote(self, something, state, props):
        
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
            self._parse_unquote(rest, state, props)


    def _parse_quote(self, something, state, props):
        """ parse everything enclosed in quotes.
        this is an easy one: just remove the escapes
        """
        if not state.read_props:
            raise ValueError, "not inside a property definition: <<%s>>" % something

        something = self.re_drop_escape.sub(lambda match: match.group(1), something )
        state.plist.append(something)

upgrade_registry.registerUpgrader(UpgradeAccessRestriction(), '0.9.3',
    AnyMetaType)

