# Copyright (c) 2002-2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: install.py,v 1.97.4.9.4.7 2004/04/22 11:39:12 philikon Exp $
"""Install for Silva Core
"""
# Python
import os

# Zope
from Globals import package_home
import zLOG
from OFS.Uninstalled import BrokenClass
from DateTime import DateTime

from Products.ProxyIndex.ProxyIndex import RecordStyle

# sibling
from Products.Silva.fssite import manage_addDirectoryView
from Products.Silva.fssite import minimalpath, expandpath
from Products.Silva.ContainerPolicy import NothingPolicy
from Products.Silva.AutoTOC import AutoTOCPolicy
from Products.Silva import roleinfo
from Products.Silva.SimpleMembership import SimpleMemberService
from Products.Silva import File
from Products.Silva import assetregistry


def add_fss_directory_view(obj, name, base, *args):
    """ add a FSS-DirectoryView object with lots of sanity checks.
    
    obj         where the new directory-object will be accessible
    name        name of the new zope object
    base        dirname(base) is taken as the base for the following
                relative path
    *args       directory names which form the relative path
                to our content directory

    This method tries to provide a sane interface independent of FSS
    path munging.

    Note that the the resulting path (joined from base and *args) must be
    below an already registered FSS-path (i.e. you must have issued
    a 'registerDirectory' on the to-be-registered directory or on one
    of its parents). 

    """
    from os.path import isdir, dirname, join, normpath, normcase

    base = dirname(base)

    # --- sanity checks ---
    if not isdir(base):
        raise ValueError, "base %s not an existing directory" % base
    abs_path = join(base, *args)
    if not isdir(abs_path):
        raise ValueError, "path %s not a directory" % abs_path
    # --- end sanity checks ---

    # we probe FSS to get the correct 'short path' to use
    fss_base = minimalpath(base)
    path = join(fss_base, *args)

    # -- sanity check --
    exp_path = expandpath(path)

    if normcase(normpath(exp_path)) != normcase(normpath(abs_path)):
        raise ValueError("detected FSS minimalpath/expandpath error, "+
                         "path: %s, FSS path: %s" % ( abs_path, exp_path ))
    # -- end sanity check --

    # -- sanity check because of FSS 1.1 createDirectoryView bug --
##     try:
##         from Products.FileSystemSite.DirectoryView import _dirreg
##         info = _dirreg.getDirectoryInfo(path)
##     except:
##         pass
##     else:
##         # XXX need to comment this out to make tests run in INSTANCE_HOME
##         # situation..
##         if info is None:
##             raise ValueError('Not a FSS registered directory: %s' % path)

    # -- end sanity check because of FSS 1.1 bug --

    # FSS should eat the path now and work correctly with it
    manage_addDirectoryView(obj, path, name)

def installFromScratch(root):
    configureProperties(root)
    configureCoreFolders(root)
    configureViews(root)
    configureSecurity(root)
    configureLayout(root)
    # now do the uinstallable stuff (views)
    install(root)
    installSilvaDocument(root)

# silva core install/uninstall are really only used at one go in refresh
def install(root):
    # if necessary, create service_resources
    # XXX this could move to installFromScratch later once all installs
    # have been upgraded
    if not hasattr(root, 'service_resources'):
        # folder containing some extra views and resources
        root.manage_addFolder('service_resources')
    # if necessary, create service_resources/Layouts
    # XXX this could move to installFromScratch later once all installs
    # have been upgraded
    if not hasattr(root.service_resources, 'Layouts'):
        #folder containing installed Layouts
        root.service_resources.manage_addFolder('Layouts')
        
    # create the core views from filesystem
    add_fss_directory_view(root.service_views, 'Silva', __file__, 'views')
    add_fss_directory_view(root.service_resources, 'Silva', __file__, 'resources')
    
    # also register views
    registerViews(root.service_view_registry)

    # add and/or update catalog
    setup_catalog(root)

    # Try to see if the Groups Product is installed.
    # If so, register the views
    try:
        from Products import Groups
    except ImportError, ie:
        pass
    else:
        registerGroupsViews(root.service_view_registry)

    # configure membership; this checks whether this is necessary
    configureMembership(root)
    # also re-configure security (XXX should this happen?)
    configureSecurity(root)

    # set up/refresh some mandatory services
    configureMiscServices(root)
    
    # forbid adding group & virtualgroup from the SMI
    root.add_silva_addable_forbidden('Silva Group')
    root.add_silva_addable_forbidden('Silva Virtual Group')
    root.add_silva_addable_forbidden('Silva IP Group')
    
    # forbid adding sqldatasources - being replaced with SilvaExternalSources
    root.add_silva_addable_forbidden('Silva SQL Data Source')

    # add or update service metadata
    configureMetadata(root)
    
    configureContainerPolicies(root)
    
    # if necessary, create service_layouts
    # XXX this could move to installFromScratch later once all installs
    # have been upgraded
    if not hasattr(root, 'service_layouts'):
        root.manage_addProduct['Silva'].manage_addLayoutService(
        'service_layouts', 'Silva Layouts Configuration')
        configure_default_layout_package(root)
    from LayoutRegistry import DEFAULT_LAYOUT
    root.set_layout(DEFAULT_LAYOUT)

    # try to install Kupu
    installKupu(root)

def configure_default_layout_package(root):
    from LayoutRegistry import DEFAULT_LAYOUT
    service_layouts = root.service_layouts
    if DEFAULT_LAYOUT not in service_layouts.get_installed_names():
        root.service_layouts.install(DEFAULT_LAYOUT)    

def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['Silva'])
    if hasattr(root, 'service_resources'):
        # XXX this can happen always if service_resources is
        # assumed to be just there in the future (like service_views)
        root.service_resources.manage_delObjects(['Silva'])
    
def is_installed(root):
    return hasattr(root.service_views, 'Silva')

def configureMetadata(root):
    from os import path
    from Products.Annotations.Extensions.SilvaInstall import install as install_annotations
    from Products.SilvaMetadata.Extensions.SilvaInstall import install as install_metadata
    from Globals import package_home
    
    # install annotations
    if not 'service_annotations' in root.objectIds():
        install_annotations(root)
    
    # install metadata
    if not 'service_metadata' in root.objectIds():    
        install_metadata(root)
    
    # load up the default metadata
    silva_home = package_home(globals())
    silva_docs = path.join(silva_home, 'doc')

    collection = root.service_metadata.getCollection()

    if not 'silva-content' in collection.objectIds():
        xml_file = path.join(silva_docs, 'silva-content.xml')
        fh = open(xml_file, 'r')        
        collection.importSet(fh)

    if not 'silva-extra' in collection.objectIds():
        xml_file = path.join(silva_docs, 'silva-extra.xml')
        fh = open(xml_file, 'r')
        collection.importSet(fh)    

    # (re) set the default type mapping
    mapping = root.service_metadata.getTypeMapping()
    default = ''
    tm = (
        {'type':'Silva Ghost Version',      'chain':''},
        {'type':'Silva Ghost Folder',       'chain':''},
        {'type':'Silva Link Version',       'chain':'silva-content, silva-extra'},
        {'type':'Silva Folder',             'chain':'silva-content, silva-extra'},
        {'type':'Silva File',               'chain':'silva-content, silva-extra'},
        {'type':'Silva Image',              'chain':'silva-content, silva-extra'},
        {'type':'Silva Indexer',            'chain':'silva-content, silva-extra'},
        {'type':'Silva Publication',        'chain':'silva-content, silva-extra'},
        {'type':'Silva Root',               'chain':'silva-content, silva-extra'},
        {'type':'Silva SQL Data Source',    'chain':'silva-content, silva-extra'},
        {'type': 'Silva AutoTOC',           'chain':'silva-content, silva-extra'},
        {'type':'Silva Group',              'chain':'silva-content, silva-extra'},
        {'type':'Silva Virtual Group',      'chain':'silva-content, silva-extra'},
        {'type':'Silva IP Group',           'chain':'silva-content, silva-extra'},
        )
    mapping.editMappings(default, tm)

    # initialize the default set if not already initialized
    for set in collection.getMetadataSets():
        if not set.isInitialized():
            set.initialize()

def configureProperties(root):
    """Configure properties on the root folder.
    XXX Probably we'll get rid of most properties in the future.
    """
    root.manage_changeProperties(title='Silva')
    property_info = [
        ('table_width', '96%', 'string'),
        ('table_cellspacing', '0', 'string'),
        ('table_cellpadding', '3', 'string'),
        ('table_border', '0', 'string'),
        ('help_url', '/%s/globals/help' % root.absolute_url(1), 'string'),
        ('comment', "This is just a place for local notes.", 'string'),
        ('access_restriction', 'allowed_ip_addresses: ALL', 'string'),
        ]
    for prop_id, value, prop_type in property_info:
        root.manage_addProperty(prop_id, value, prop_type)

def configureCoreFolders(root):
    """A bunch of core directory views.
    """
    # images, stylesheets, etc
    add_fss_directory_view(root, 'globals', __file__, 'globals')
    # folder containing some extra views and resources
    root.manage_addFolder('service_resources', 'Silva Product Resources')

def configureViews(root):
    """The view infrastructure for Silva.
    """
    # view registry
    root.manage_addProduct['SilvaViews'].manage_addMultiViewRegistry(
        'service_view_registry')
    root.manage_addProduct['Silva'].manage_addExtensionService(
        'service_extensions', 'Silva Product and Extension Configuration')
    # folder contains the various view trees
    root.manage_addFolder('service_views', 'Silva View Machinery')
    # and set Silva tree
    # (does not need to be more polite to extension packages;
    #  they will be installed later on)
    root.service_view_registry.set_trees(['Silva'])

def configureMiscServices(root):
    """Set up some services which did not fit elsewhere """
    # add service_files if it doesn't exist
    if not hasattr(root, 'service_files'):
        File.manage_addFilesService(root, 'service_files', 
            'Silva Files Service', filesystem_path='var/repository')    
    # do the same for the sidebar service
    if not hasattr(root, 'service_sidebar'):
        root.manage_addProduct['Silva'] \
            .manage_addSidebarService('service_sidebar', 
            'Silva Content Tree Navigation')

def configureSecurity(root):
    """Update the security tab settings to the Silva defaults.
    """
    # add the appropriate roles if necessary
    userdefined_roles = root.userdefined_roles()
    request = root.REQUEST
    request.set('URL1', '')
    for role in roleinfo.ASSIGNABLE_ROLES:
        if role not in userdefined_roles:
            request.set('role', role)
            root.manage_defined_roles(submit='Add Role', REQUEST=request)

    # now configure permissions
    
    add_permissions = [
        'Add Documents, Images, and Files',
        'Add Silva Folders',
        'Add Silva Ghost Versions',
        'Add Silva Ghosts',
        'Add Silva Links',
        'Add Silva Link Versions',
        'Add Silva Images',
        'Add Silva Files',        
        ]
    
    for add_permission in add_permissions:
        root.manage_permission(add_permission, roleinfo.AUTHOR_ROLES)

    # chief editor can customize a layout
    root.manage_permission('Add Page Templates', roleinfo.CHIEF_ROLES)
    root.manage_permission('Add Folders', roleinfo.CHIEF_ROLES)

    # chief editors and up may also place groups and Datasources.
    root.manage_permission('Add Silva Groups', roleinfo.CHIEF_ROLES)
    root.manage_permission('Add Silva Virtual Groups', roleinfo.CHIEF_ROLES)
    root.manage_permission('Add Silva IP Groups', roleinfo.CHIEF_ROLES)
    root.manage_permission('Add Silva SQL Data Sources', roleinfo.CHIEF_ROLES)
    
    # everybody may view root by default XXX
    # (is this bad in case of upgrade/refresh)
    root.manage_permission('View', roleinfo.ALL_ROLES)
  
    # person with viewer role can do anything that anonymous does + has
    # additional right to view when anonymous can't. This means zope
    # should fall back on permissions for anonymous in case viewer does
    # not have these permissions. That's why we don't have to assign them
    # to viewer.
    root.manage_permission('Add Silva Publications', roleinfo.EDITOR_ROLES)
    root.manage_permission('Add Silva Ghost Folders', roleinfo.EDITOR_ROLES)
    root.manage_permission('Add Silva Indexers', roleinfo.EDITOR_ROLES)
    root.manage_permission('Approve Silva content', roleinfo.EDITOR_ROLES)
    root.manage_permission('Change Silva access', roleinfo.CHIEF_ROLES)
    root.manage_permission('Change Silva content', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Manage properties', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Add Silva AutoTOCs', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Read Silva content', roleinfo.READER_ROLES)
    # authenticated needs this permission as we are not
    # allowed to use service_editor otherwise
    root.manage_permission('Use XMLWidgets Editor Service',
                           roleinfo.READER_ROLES + ('Authenticated',))

    # this is necessary to let authors use external editor
    try:
        root.manage_permission('Use external editor', roleinfo.AUTHOR_ROLES)
    # hail to Zope and its string exceptions!!
    except:
        pass

    # Set permissions/roles for Groups Service
    # XXX this is a bit of a hack, as Groups may not be installed we
    # catch exceptions. A 'refresh' after Groups is installed should
    # set the permissions right
    try:
        root.manage_permission('Access Groups information',
                               roleinfo.READER_ROLES)
        root.manage_permission('Access Group mappings',
                               roleinfo.READER_ROLES)
        root.manage_permission('Change Groups', roleinfo.CHIEF_ROLES)
        root.manage_permission('Change Group mappings', roleinfo.CHIEF_ROLES)
    except:
        pass

def configureLayout(root, default_if_existent=0):
    """Install common layout code into root.
    If the default_if_existent argument is true, ids will be prefixed with 
    default_ if the id already exists in the root.
    """
    for id in ['layout_macro.html', 'content.html', 'rename-to-override.html',
               'standard_error_message', 'standard_unauthorized_message',
               'copyright',]:
        add_helper(root, id, globals(), zpt_add_helper, default_if_existent)

    for id in ['index_html.py', 'preview_html.py', 'surroundlinks.py',
               'get_metadata_element.py', 'get_layout_macro.py', ]:
        add_helper(root, id, globals(), py_add_helper, default_if_existent)
        
    add_helper(root, 'frontend.css', globals(), dtml_add_helper, default_if_existent)

def configureMembership(root):
    """Install membership code into root.
    """
    # add member service and message service
    ids = root.objectIds()
    if 'service_members' not in ids:
        root.manage_addProduct['Silva'].manage_addSimpleMemberService(
            'service_members', 'Silva Membership Service')
        
    if 'Members' not in ids:
        root.manage_addFolder('Members')

    if 'service_messages' not in ids:
        root.manage_addProduct['Silva'].manage_addEmailMessageService(
            'service_messages', 'Silva Message Service')

# helpers to add various objects to the root from the layout directory
# these won't add FS objects but genuine ZMI managed code
def add_helper(root, id, info, add_func, default_if_existent=0, folder='layout'):
    filename = id
    if add_func == py_add_helper or add_func == pt_add_helper:
        id = os.path.splitext(id)[0]
    if default_if_existent and hasattr(root.aq_base, id):
        id = 'default_' + id
    text = read_file(filename, info, folder)
    add_func(root, id, text)

def pt_add_helper(root, id, text):
    if hasattr(root.aq_base, id):
        getattr(root, id).write(text)
    else:
        root.manage_addProduct['PageTemplates'].manage_addPageTemplate(
            id, text=text)

def zpt_add_helper(root, id, text):
    if hasattr(root.aq_base, id):
        getattr(root, id).write(text)
    else:
        root.manage_addProduct['PageTemplates'].manage_addPageTemplate(
            id, text=text)

def dtml_add_helper(root, id, text):
    if hasattr(root.aq_base, id):
        getattr(root, id).manage_edit(text, '')
    else:
        root.manage_addDTMLMethod(id, file=text)

def py_add_helper(root, id, text):
    if hasattr(root.aq_base, id):
        getattr(root, id).write(text)
    else:
        root.manage_addProduct['PythonScripts'].manage_addPythonScript(id)
        getattr(root, id).write(text)

def read_file(id, info, folder):
    filename = os.path.join(package_home(info), folder, id)
    f = open(filename, 'rb')
    text = f.read()
    f.close()
    return text

def registerViews(reg):
    """Register core views on registry.
    """
    # edit
    reg.register('edit', 'Silva Folder',
                 ['edit', 'Container', 'Folder'])
    reg.register('edit', 'Silva Root',
                 ['edit', 'Container', 'Publication'])
    reg.register('edit', 'Silva Publication',
                 ['edit', 'Container', 'Publication'])
    reg.register('edit', 'Silva Ghost',
                 ['edit', 'VersionedContent', 'Ghost'])
    reg.register('edit', 'Silva Link',
                 ['edit', 'VersionedContent', 'Link'])
    reg.register('edit', 'Silva Image',
                 ['edit', 'Asset', 'Image'])
    reg.register('edit', 'Silva File',
                 ['edit', 'Asset', 'File'])
    reg.register('edit', 'Silva Indexer',
                 ['edit', 'Content', 'Indexer'])
    reg.register('edit', 'Silva SQL Data Source',
                 ['edit', 'Asset', 'SQLDataSource'])
    reg.register('edit', 'Silva Simple Member',
                 ['edit', 'Member', 'SimpleMember'])
    reg.register('edit', 'Silva Ghost Folder',
                 ['edit', 'Container', 'GhostFolder'])
    reg.register('edit', 'Silva AutoTOC', 
                 ['edit', 'Content', 'AutoTOC'])
    
    # public
    reg.register('public', 'Silva Folder', ['public', 'Folder'])
    reg.register('public', 'Silva Publication', ['public', 'Folder'])
    reg.register('public', 'Silva Root', ['public', 'Folder'])
    reg.register('public', 'Silva Ghost', ['public', 'Ghost'])
    reg.register('public', 'Silva Link', ['public', 'Link'])
    reg.register('public', 'Silva Image', ['public', 'Image'])
    reg.register('public', 'Silva File', ['public', 'File'])
    reg.register('public', 'Silva Indexer', ['public', 'Indexer'])
    reg.register('public', 'Silva SQL Data Source',
                 ['public', 'SQLDataSource'])
    reg.register('public', 'Silva Ghost Folder', ['public', 'Folder'])
    reg.register('public', 'Silva AutoTOC', ['public', 'AutoTOC'])

    # add
    reg.register('add', 'Silva Folder', ['add', 'Folder'])
    reg.register('add', 'Silva Publication', ['add', 'Publication'])
    reg.register('add', 'Silva Ghost', ['add', 'Ghost'])
    reg.register('add', 'Silva Link', ['add', 'Link'])
    reg.register('add', 'Silva Image', ['add', 'Image'])
    reg.register('add', 'Silva File', ['add', 'File'])
    reg.register('add', 'Silva Indexer', ['add', 'Indexer'])
    reg.register('add', 'Silva SQL Data Source', ['add', 'SQLDataSource'])
    reg.register('add', 'Silva Ghost Folder', ['add', 'GhostFolder'])
    reg.register('add', 'Silva AutoTOC', ['add', 'AutoTOC'])

def registerGroupsViews(reg):
    """Register groups views on registry.
    """
    reg.register(
        'edit', 'Silva Group', ['edit', 'Asset', 'Groups', 'Group'])
    reg.register(
        'edit', 'Silva Virtual Group', ['edit', 'Asset', 'Groups', 'VirtualGroup'])
    reg.register(
        'edit', 'Silva IP Group', ['edit', 'Asset', 'Groups', 'IPGroup'])
    reg.register('add', 'Silva Group', ['add', 'Groups', 'Group'])
    reg.register('add', 'Silva Virtual Group', ['add', 'Groups', 'VirtualGroup'])
    reg.register('add', 'Silva IP Group', ['add', 'Groups', 'IPGroup'])

def unregisterViews(reg):
    for meta_type in ['Silva Folder',
                      'Silva Publication',
                      'Silva Ghost',
                      'Silva Image',
                      'Silva DemoObject',
                      'Silva File',
                      'Silva Indexer',
                      'Silva SQL Data Source',
                      'Silva Group',
                      'Silva Virtual Group',
                      'Silva IP Group',
                      'Silva Ghost Folder']:
        reg.unregister('edit', meta_type)
        reg.unregister('public', meta_type)
        reg.unregister('add', meta_type)
    reg.unregister('edit', 'Silva Root')
    reg.unregister('public', 'Silva Root')
    reg.unregister('edit', 'Silva Simple Member')
    # next line for hysterical reasons, should go away 
    reg.unregister('public', 'Silva Simple Member')

class El:
    """Helper class to initialize the catalog lexicon
    """
    def __init__(self, **kw):
        self.__dict__.update(kw)

def setup_catalog(silva_root):
    """Sets up the ZCatalog
    """
    # See if catalog exists, if not create one
    if not hasattr(silva_root, 'service_catalog'):
        silva_root.manage_addProduct['ZCatalog'].manage_addZCatalog(
            'service_catalog', 'Silva Service Catalog')

    catalog = silva_root.service_catalog
    lexicon_id = 'silva_lexicon'

    # Add lexicon with right splitter (Silva.UnicodeSplitter.Splitter 
    # registers under "Unicode Whitespace splitter")
    if not lexicon_id in catalog.objectIds():
        # XXX ugh, hardcoded dependency on names in ZCTextIndex
        catalog.manage_addProduct['ZCTextIndex'].manage_addLexicon(
            lexicon_id, 
            elements=[
            El(group='Case Normalizer', name='Case Normalizer'),
            El(group='Stop Words', name=" Don't remove stop words"),
            El(group='Word Splitter', name="Unicode Whitespace splitter"),
            ]
            )

    existing_columns = catalog.schema()
    columns = [
        'id', 
        'meta_type', 
        'silva_object_url',
        ]

    for column_name in columns:
        if column_name in existing_columns:
            continue
        catalog.addColumn(column_name)

    existing_indexes = catalog.indexes()
    indexes = [
        ('id', 'FieldIndex'),
        ('meta_type', 'FieldIndex'),
        ('path', 'PathIndex'),
        ('fulltext', 'ZCTextIndex'),        
        ('version_status', 'FieldIndex'),
        ]

    for field_name, field_type in indexes:
        if field_name in existing_indexes:
            continue

        # special handling for argument passing to zctextindex
        # ranking algorithm used is best for larger text body / query size ratios
        if field_type == 'ZCTextIndex':
            extra = RecordStyle(
                {'doc_attr':field_name,
                 'lexicon_id':'silva_lexicon',
                 'index_type':'Okapi BM25 Rank'}
                )
            catalog.addIndex(field_name, field_type, extra)
            continue
        
        catalog.addIndex(field_name, field_type)

    # if the silva root has an index_object attribute, add it to the catalog
    if hasattr(silva_root, 'index_object'):
        silva_root.index_object()

def configureContainerPolicies(root):
    # create container policy registry
    if not hasattr(root, 'service_containerpolicy'):
        root.manage_addProduct['Silva'] \
            .manage_addContainerPolicyRegistry()
    cpr = root.service_containerpolicy
    cpr.register('None', NothingPolicy, 0)
    cpr.register('Auto TOC', AutoTOCPolicy, 0)

def installSilvaDocument(root):
    # installs Silva Document if available
    # see issue #536 and #611
    from Products.Silva.ExtensionRegistry import extensionRegistry
    if 'SilvaDocument' not in extensionRegistry.get_names():
        return 
    root.service_extensions.install('SilvaDocument')
    # create the demo content:
    root.sec_update_last_author_info()
    root.manage_addProduct['SilvaDocument'].manage_addDocument('index',
        'Welcome to Silva!')
    doc = root.index
    doc.sec_update_last_author_info()
    version = doc.get_editable()
    version.content.manage_edit('<doc><p type="normal">Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <link url="edit">click this link</link>).</p></doc>')
    doc.set_unapproved_version_publication_datetime(DateTime())
    doc.approve_version()

def installKupu(root):
    try:
        from Products import kupu
    except:
        pass
    else:
        if not hasattr(root, 'kupu'):
            add_fss_directory_view(root, 'kupu', kupu.__file__, 'common')
        if not hasattr(root, 'kupu_silva'):
            add_fss_directory_view(root, 'kupu_silva', kupu.__file__, 'silva')

if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
