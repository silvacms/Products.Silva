from __future__ import nested_scopes
from ISilvaObject import ISilvaObject
from IContainer import IContainer
from IVersionedContent import IVersionedContent, ICatalogedVersionedContent
from IVersion import IVersion, ICatalogedVersion
from Membership import NoneMember, noneMember 
from helpers import check_valid_id

def check_reserved_ids(obj):
    """Walk through the entire tree to find objects of which the id is not
    allowed, and return a list of the urls of those objects
    """
    illegal_urls = []
    for o in obj.objectValues():
        if not check_valid_id(obj, str(o.id), 1):
            print 'Illegal url found:', o.absolute_url()
            illegal_urls.append(o.absolute_url())
        if hasattr(o, 'objectValues'):
            illegal_urls += check_reserved_ids(o)
    return illegal_urls

illegal_url_template = '''
The following objects have an id that is illegal in
Silva, and need to be renamed in order for the upgrade to continue:<br /><br />
%s
'''

def from091to092(self, root):
    """Upgrade Silva content from 0.9.1 to 0.9.2
    """
    # the manage_beforeDelete of the original Document doesn't work, since the 
    # code will look for a 'content' attribute, which doesn't yet exist on 
    # them, therefore we're going to have to do some trickery here...
    # This is a nasty piece of monkeypatching, mainly because other functionality
    # might require the original use of manage_beforeDelete somewhere, and
    # it isn't possible to monkeypatch the object since no reference to the object
    # can be used in monkeypatched object methods (self is not passed as a variable to
    # those methods)
    from Document import Document

    old_manage_beforeDelete = Document.manage_beforeDelete
    def manage_beforeDelete_old_style_docs(self, item, container):
        Document.inheritedAttribute('manage_beforeDelete')(self, item, container)
    Document.manage_beforeDelete = manage_beforeDelete_old_style_docs

    print 'Going to check ids'

    # first check the object tree for illegal ids, since they will break the upgrade
    illegal_urls = check_reserved_ids(root)

    if illegal_urls:
        urllist = []
        for url in illegal_urls:
            urllist.append('<a href="%(url)s">%(url)s</a><br />' % {'url': url})
        return illegal_url_template % '\n'.join(urllist)

    print 'Going to upgrade'

    # set the '_allow_subscription' attribute on servce_members if it isn't there yet
    sm = getattr(root, 'service_members', None)
    if sm is not None:
        sm._allow_subscription = 0
    
    try:
        upgrade_using_registry(root, '0.9.2')
    finally:
        Document.manage_beforeDelete = old_manage_beforeDelete

def from09to091(self, root):
    """Upgrade Silva from 0.9 to 0.9.1
    """
    # upgrade member objects in the site if they're still using the old system
    upgrade_memberobjects(root)
    # upgrade xml in the site
    upgrade_using_registry(root, '0.9.1')
    
def from086to09(self, root):
    """Upgrade Silva from 0.8.6(.1) to 0.9.
    """
    id = root.id
    # Put a copy of the current Silva Root in a backup folder.
    backup_id = id + '_086'
    self.manage_addFolder(backup_id)
    cb = self.manage_copyObjects([id])
    backup_folder = getattr(self, backup_id)
    backup_folder.manage_pasteObjects(cb_copy_data=cb)
    # Delete and re-install the DirectoryViews
    from install import add_fss_directory_view
    root.service_views.manage_delObjects(['Silva'])
    add_fss_directory_view(root.service_views, 'Silva', __file__, 'views')
    root.manage_delObjects([
        'globals', 'service_utils', 'service_widgets'])       
    add_fss_directory_view(root, 'globals', __file__, 'globals')
    add_fss_directory_view(root, 'service_utils', __file__, 'service_utils')
    add_fss_directory_view(root, 'service_widgets', __file__, 'widgets')

def from085to086(self, root):
    """Upgrade Silva from 0.8.5 to 0.8.6 as a simple matter of programming.
    """
    # rename silva root so we can drop in fresh new one
    id = root.id
    backup_id = id + '_085'
    self.manage_renameObject(id, backup_id)
    orig_root = getattr(self, backup_id)
    # create new silva root
    self.manage_addProduct['Silva'].manage_addRoot(id, orig_root.title)
    dest_root = getattr(self, id)
    # wipe out layout stuff from root as we're going to copy it over
    delete_ids = [obj.getId() for obj in dest_root.objectValues() if
                  obj.meta_type in ['DTML Method', 'Script (Python)', 'Page Template']]
    dest_root.manage_delObjects(delete_ids)

    # now copy over silva contents from old root; everything should be a
    # SilvaObject
    copy_ids = [obj.getId() for obj in orig_root.objectValues() if
                ISilvaObject.isImplementedBy(obj)]
    cb = orig_root.manage_copyObjects(copy_ids)
    dest_root.manage_pasteObjects(cb_copy_data=cb)

    # also copy over layout stuff and various services
    layout_ids = [obj.getId() for obj in orig_root.objectValues() if
                  obj.meta_type in ['DTML Method', 'Script (Python)', 'Page Template']  or \
                  obj.getId() in ('service_groups', 'service_files', 'service_mailhost', 'service_catalog') ]

    other_ids = [obj.getId() for obj in orig_root.objectValues() if
                 obj.meta_type not in ['DTML Method', 'Script (Python)', 'Page Template', \
                                       'Silva View Registry', 'XMLWidgets Editor Service', 'XMLWidgets Registry'] \
                 and obj.getId() not in ['globals', 'service_utils', 'service_setup', 'service_widgets', 'service_groups', 'service_files'] \
                 and not ISilvaObject.isImplementedBy(obj) ]

    
    cb = orig_root.manage_copyObjects(layout_ids)
    dest_root.manage_pasteObjects(cb_copy_data=cb)

    # now to copy over properties

    # figure out what changed
    dest_properties = dest_root.propertyIds()
    new_properties = []
    changed_properties = []
    for id in orig_root.propertyIds():
        if id in dest_properties:
            changed_properties.append(id)
        else:
            new_properties.append(id)
    # alter properties that need to be altered
    for id in changed_properties:
        dest_root.manage_changeProperties({id: orig_root.getProperty(id)})
    # add properties that need to be added
    for id in new_properties:
        dest_root.manage_addProperty(id, orig_root.getProperty(id),
                                     orig_root.getPropertyType(id))
    
    # now copy over the roles information
    if hasattr(orig_root, '__ac_local_roles__'):
        dest_root.__ac_local_roles__ = orig_root.__ac_local_roles__
    if hasattr(orig_root, '__ac_local_groups__'):
        dest_root.__ac_local_groups__ = orig_root.__ac_local_groups__

    # if there's an 'acl_users', 'images', or 'locals' copy that over as well.
    to_copy_ids = []
    for id in ['acl_users', 'images', 'locals']:
        if hasattr(orig_root.aq_base, id):
            to_copy_ids.append(id)
            if id in other_ids:
                other_ids.remove(id)
    cb = orig_root.manage_copyObjects(to_copy_ids)
    dest_root.manage_pasteObjects(cb_copy_data=cb)

    # copy over order information
    dest_root._ordered_ids = orig_root._ordered_ids
    
    # we still may not have everything, but a good part..
    # should advise the upgrader to copy over the rest by hand
    
    return other_ids

def upgrade_memberobjects(obj):
    service_members = obj.service_members
    for o in obj.aq_explicit.objectValues():
        info = getattr(o, '_last_author_info', None)
        if info is not None and type(info) == type({}):
            if info.has_key('uid'):
                o._last_author_info = service_members.get_cached_member(
                    info['uid'])
            else:
                o._last_author_info = noneMember
        if IContainer.isImplementedBy(o):
            upgrade_memberobjects(o)

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
        
#-----------------------------------------------------------------------------
# Upgrade registry, this will be used to upgrade versions >= 0.9.1
#-----------------------------------------------------------------------------

def upgrade_using_registry(obj, version):
    """Upgrades obj recursively for a specific Silva version
    """
    for o in obj.objectValues():
        mt = o.meta_type
        if upgrade_registry.is_registered(mt, version):
            for upgrade in upgrade_registry.get_meta_type(mt, version):
                print 'Going to run %s on %s' % (upgrade, obj.absolute_url())
                res = upgrade(o)
                # sometimes upgrade methods will replace objects, if so the
                # new object should be returned so that can be used for the rest
                # of the upgrade chain instead of the old (probably deleted) one
                if res:
                    o = res
        if hasattr(o, 'objectValues'):
            #print 'Going to descend into', o.id
            upgrade_using_registry(o, version)

class UpgradeRegistry:
    """Here people can register upgrade methods for their objects
    """
    def __init__(self):
        self.__registry = {}
    
    def register(self, meta_type, upgrade_handler, version):
        """Register a meta_type for upgrade.

        The upgrade handler is called with the object as its only argument
        when the upgrade script encounters an object of the specified
        meta_type.
        """
        if not self.__registry.has_key(meta_type):
            self.__registry[meta_type] = {}
        if not self.__registry[meta_type].has_key(version):
            self.__registry[meta_type][version] = []
        self.__registry[meta_type][version].append(upgrade_handler)

    def get_meta_type(self, meta_type, version):
        """Return the registered upgrade_handlers of meta_type
        """
        #print 'Going to return upgrades for %s: %s' % (meta_type, version)
        #print 'Upgrades:', self.__registry[meta_type][version]
        return self.__registry[meta_type][version]

    def is_registered(self, meta_type, version):
        """Returns whether the meta_type is registered"""
        return self.__registry.has_key(meta_type) and self.__registry[meta_type].has_key(version)

upgrade_registry = UpgradeRegistry()

#-----------------------------------------------------------------------------
# Upgrade functions using the upgrade registry
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# 0.9 to 0.9.1
#-----------------------------------------------------------------------------

# Some upgrade stuff
def upgrade_document_091(obj):
    for o in obj.objectValues():
        if o.meta_type == 'Silva Document Version':
            upgrade_list_titles_in_parsed_xml(o.content.documentElement)

def upgrade_demoobject_091(obj):
    for o in obj.objectValues():
        if o.meta_type == 'Silva DemoObject Version':
            upgrade_list_titles_in_parsed_xml(o.content.documentElement)

upgrade_registry.register('Silva Document', upgrade_document_091, '0.9.1')
upgrade_registry.register('Silva DemoObject', upgrade_demoobject_091, '0.9.1')

#-----------------------------------------------------------------------------
# 0.9.1 to 0.9.2
#-----------------------------------------------------------------------------

# This is a complicated set of upgrades!! The order of the upgrades is important
# (they are called in the order in which they are registered), because most
# methods expect objects to be a certain type and the type can change somewhere
# in the chain of methods (old-style ParsedXML versions are converted to Version
# objects, which means that the way to perform certain actions on them changes)

from StringIO import StringIO

# small helper function to get the xml from an old-style version
def get_version_xml(obj, version):
    v = getattr(obj, version, None)
    if v is None:
        raise Exception, 'No version %s!' % version
    s = StringIO()
    v.documentElement.writeStream(s)
    return s.getvalue().encode('UTF8')

from Document import DocumentVersion

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
            
    for version in ['unapproved', 'approved', 'public', 'last_closed']:
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
        for versionid, pdt, edt in obj._previous_versions[:-1]:
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
set_el_name_mapping = {'silva-content': {'short_title': 'shorttitle',
                                    },
                        'silva-extra': {'document_comment': 'comment', 
                                        'container_comment': 'comment',
                                        'contact_email': 'contactemail',
                                        'contact_name': 'contact_name',
                                    }
                    }

# some helper function
def get_versions_or_self(obj):
    #print 'Getting versions of', obj.id
    ret = []
    if (IVersionedContent.isImplementedBy(obj) or
            ICatalogedVersionedContent.isImplementedBy(obj)):
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

def unicode_and_metadata_092(obj):
    # get the metadata sets for the object
    ms = obj.service_metadata

    values = {}
    for set_name, el_name_mapping in set_el_name_mapping.items():
        for old_name, new_name in el_name_mapping.items():
            #print 'Testing for', old_name, 'on object', obj.absolute_url()
            old_value = obj.getProperty(old_name)
            if old_value is None:
                old_value = getattr(obj.aq_inner, old_name, None)
                if old_value is None:
                    #print 'Not found'
                    continue
                if callable(old_value):
                    old_value = old_value()
                if old_value is None:
                    #print 'Not found'
                    continue
            #print 'Old value:', old_value
            # if somehow the string is already unicode (who knows, right :)
            # skip conversion
            new_value = old_value
            if type(old_value) != type(u' '):
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
    if not '_title' in obj.aq_base.__dict__.keys():
        return
    title = obj._title
    del obj._title
    if type(title) != type(u''):
        title = unicode(title, 'cp1252', 'replace')
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

def replace_object_title_092(obj):
    """Move the title to the metadata
    """
    #print 'Replace object title for', obj.id
    if not '_title' in obj.aq_base.__dict__.keys():
        #print 'No title available on', obj.absolute_url()
        return
    #print obj.absolute_url()
    title = obj.aq_inner._title
    #print 'Title:', title.encode('ascii', 'replace')
    #print 'Plain title attribute:', obj.aq_inner.title
    #print dir(obj.aq_inner)
    #print obj.aq_base.__dict__
    del obj.aq_inner._title
    if type(title) != type(u''):
        title = unicode(title, 'cp1252', 'replace')
    objects = get_versions_or_self(obj)
    for object in objects:
        #print 'Going to replace title of version', object.getPhysicalPath()
        #print 'New title:', title.encode('ascii', 'replace')
        object.set_title(title)
        #print type(title)
        #print type(object.title)

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
    """Do initial catalogin of objects"""
    #print 'Catalog', obj.getPhysicalPath()
    if ((IVersion.isImplementedBy(obj) or ICatalogedVersion.isImplementedBy(obj)) and
            obj.id not in obj.aq_parent._get_indexable_versions()):
        return
    #if hasattr(obj, 'content'):
        #print 'Type of content:', type(obj.content_xml())
        #print 'Fulltext:', type(obj.fulltext())
        #print 'Title:', type(obj.title)
    obj.index_object()
    
upgrade_registry.register('Silva Root', catalog_092, '0.9.2')
upgrade_registry.register('Silva Folder', catalog_092, '0.9.2')
upgrade_registry.register('Silva Publication', catalog_092, '0.9.2')
upgrade_registry.register('Silva Document Version', catalog_092, '0.9.2')
upgrade_registry.register('Silva DemoObject Version', catalog_092, '0.9.2')
upgrade_registry.register('Silva Ghost Version', catalog_092, '0.9.2')

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

