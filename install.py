"""Install for Silva Core
"""

from Globals import package_home
import os

import EditorSupportNested
import File
from Products.FileSystemSite.DirectoryView import manage_addDirectoryView
from Products.FileSystemSite.utils import minimalpath, expandpath
from Products.ProxyIndex.ProxyIndex import RecordStyle

from SimpleMembership import SimpleMemberService

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
    try:
        from Products.FileSystemSite.DirectoryView import _dirreg
        info = _dirreg.getDirectoryInfo(path)
    except:
        pass
    else:
        # XXX need to comment this out to make tests run in INSTANCE_HOME
        # situation..
        if info is None:
            raise ValueError('Not a FSS registered directory: %s' % path)

    # -- end sanity check because of FSS 1.1 bug --

    # FSS should eat the path now and work correctly with it
    manage_addDirectoryView(obj, path, name)

def installFromScratch(root):
    configureProperties(root)
    configureCoreFolders(root)
    configureViews(root)
    configureXMLWidgets(root)
    configureSecurity(root)
    configureLayout(root)
    # now do the uinstallable stuff (views)
    install(root)

# silva core install/uninstall are really only used at one go in refresh
def install(root):
    # if necessary, create service_resources
    # XXX this could move to installFromScratch later once all installs
    # have been upgraded
    if not hasattr(root, 'service_resources'):
        # folder containing some extra views and resources
        root.manage_addFolder('service_resources')
        
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
    # and reconfigure xml widget registries
    # FIXME: should we check if the registries exist?
    # (for upgrading, and maybe to handle accidential deletion)
    registerCoreWidgets(root)

    # set up/refresh some mandatory services
    configureMiscServices(root)
    
    # forbid adding group & virtualgroup from the SMI
    root.add_silva_addable_forbidden('Silva Group')
    root.add_silva_addable_forbidden('Silva Virtual Group')

    # add or update service metadata
    configureMetadata(root)
    
def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['Silva'])
    if hasattr(root, 'service_resources'):
        # XXX this can happen always if service_resources is
        # assumed to be just there in the future (like service_views)
        root.service_resources.manage_delObjects(['Silva'])
    try:
        root.manage_delObjects(['service_editorsupport'])
    except 'BadRequest':
        pass
    
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
        {'type':'Silva Document Version',   'chain':'silva-content, silva-extra'},
        {'type':'Silva DemoObject Version', 'chain':'silva-content, silva-extra'},
        {'type':'Silva Ghost Version',      'chain':''},
        {'type':'Silva Folder',             'chain':'silva-extra'},
        {'type':'Silva File',               'chain':'silva-content, silva-extra'},
        {'type':'Silva Image',              'chain':'silva-content, silva-extra'},
        {'type':'Silva Indexer',            'chain':'silva-content, silva-extra'},
        {'type':'Silva Publication',        'chain':'silva-extra'},
        {'type':'Silva Root',               'chain':'silva-extra'},
        {'type':'Silva SQL Data Source',    'chain':'silva-content, silva-extra'},
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
    # commonly used python scripts (XXX probably should go away)
    add_fss_directory_view(root, 'service_utils', __file__, 'service_utils')

    # folder containing some extra views and resources
    root.manage_addFolder('service_resources', 'Silva Product Resources')

def configureViews(root):
    """The view infrastructure for Silva.
    """
    # view registry
    root.manage_addProduct['Silva'].manage_addMultiViewRegistry(
        'service_view_registry')
    root.manage_addProduct['Silva'].manage_addExtensionService(
        'service_extensions', 'Silva Product Extension Configuration')
    # folder contains the various view trees
    root.manage_addFolder('service_views', 'Silva View Machinery')
    # and set Silva tree
    # (does not need to be more polite to extension packages;
    #  they will be installed later on)
    root.service_view_registry.set_trees(['Silva'])

def configureMiscServices(root):
    """Set up some services which did not fit elsewhere """
    # add editor support service
    EditorSupportNested.manage_addEditorSupport(root)
    # add service_files if it doesn't exist
    if not hasattr(root, 'service_files'):
        File.manage_addFilesService(root, 'service_files', 
            'Silva Files Service', filesystem_path='var/repository')    
    # do the same for the sidebar service
    if not hasattr(root, 'service_sidebar'):
        root.manage_addProduct['Silva'] \
            .manage_addSidebarService('service_sidebar', 'Silva Content Tree Navigation')


def configureSecurity(root):
    """Update the security tab settings to the Silva defaults.
    """
    # add the appropriate roles if necessary
    roles = ['Viewer', 'Reader', 'Author', 'Editor', 'ChiefEditor']
    userdefined_roles = root.userdefined_roles()
    request = root.REQUEST
    for role in roles:
        if role not in userdefined_roles:
            request.set('role', role)
            root.manage_defined_roles(submit='Add Role', REQUEST=request)

    # now configure permissions
    all_reader = ['Reader', 'Author', 'Editor',
                  'ChiefEditor', 'Manager']
    all_author = ['Author', 'Editor', 'ChiefEditor', 'Manager']
    all_editor = ['Editor', 'ChiefEditor', 'Manager']
    all_chief = ['ChiefEditor', 'Manager']
    
    add_permissions = [
        'Add Documents, Images, and Files',
        'Add Silva DemoObject Versions',
        'Add Silva DemoObjects',
        'Add Silva Documents',
        'Add Silva Folders',
        'Add Silva Ghost Versions',
        'Add Silva Ghosts',
        'Add Silva Images',
        'Add Silva Files',        
        ]
    
    for add_permission in add_permissions:
        root.manage_permission(add_permission, all_author)

    # chief editors and up may also place groups and Datasources.
    root.manage_permission('Add Silva Groups', all_chief)
    root.manage_permission('Add Silva Virtual Groups', all_chief)
    root.manage_permission('Add Silva SQL Data Sources', all_chief)
    
    # everybody may view root by default XXX
    # (is this bad in case of upgrade/refresh)
    root.manage_permission('View',
                           all_reader +
                           ['Anonymous', 'Authenticated', 'Viewer'])
    # person with viewer role can do anything that anonymous does + has
    # additional right to view when anonymous can't. This means zope
    # should fall back on permissions for anonymous in case viewer does
    # not have these permissions. That's why we don't have to assign them
    # to viewer.
    root.manage_permission('Add Silva Publications', all_editor)
    root.manage_permission('Add Silva Indexers', all_editor)
    root.manage_permission('Approve Silva content', all_editor)
    root.manage_permission('Change Silva access', all_chief)
    root.manage_permission('Change Silva content', all_author)
    root.manage_permission('Manage properties', all_author)
    root.manage_permission('Read Silva content', all_reader)
    # authenticated needs this permission as we are not
    # allowed to use service_editor otherwise
    root.manage_permission('Use XMLWidgets Editor Service',
                           all_reader + ['Authenticated'])

    # Set permissions/roles for Groups Service
    # XXX this is a bit of a hack, as Groups may not be installed we
    # catch exceptions. A 'refresh' after Groups is installed should
    # set the permissions right
    try:
        root.manage_permission('Access Groups information', all_reader)
        root.manage_permission('Access Group mappings', all_reader)
        root.manage_permission('Change Groups', all_chief)
        root.manage_permission('Change Group mappings', all_chief)
    except:
        pass

def configureLayout(root, default_if_existent=0):
    """Install layout code into root.
    If the default_if_existent argument is true, ids will be prefixed with 
    default_ if the id already exists in the root.
    """
    for id in ['layout_macro.html', 'content.html', 'rename-to-override.html',
               'standard_error_message', 'standard_unauthorized_message', ]:
        add_helper(root, id, globals(), zpt_add_helper, default_if_existent)

    for id in ['index_html.py', 'index_html_restricted.py', 'preview_html.py',
               'get_metadata_element.py']:
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
    reg.register('edit', 'Silva Document',
                 ['edit', 'VersionedContent', 'Document'])
    reg.register('edit', 'Silva Root',
                 ['edit', 'Container', 'Publication'])
    reg.register('edit', 'Silva Publication',
                 ['edit', 'Container', 'Publication'])
    reg.register('edit', 'Silva Ghost',
                 ['edit', 'VersionedContent', 'Ghost'])
    reg.register('edit', 'Silva Image',
                 ['edit', 'Asset', 'Image'])
    reg.register('edit', 'Silva DemoObject',
                 ['edit', 'VersionedContent', 'DemoObject'])
    reg.register('edit', 'Silva File',
                 ['edit', 'Asset', 'File'])
    reg.register('edit', 'Silva Indexer',
                 ['edit', 'Content', 'Indexer'])
    reg.register('edit', 'Silva SQL Data Source',
                 ['edit', 'Asset', 'SQLDataSource'])
    reg.register('edit', 'Silva Simple Member',
                 ['edit', 'Member', 'SimpleMember'])
    
    # public
    reg.register('public', 'Silva Folder', ['public', 'Folder'])
    reg.register('public', 'Silva Publication', ['public', 'Folder'])
    reg.register('public', 'Silva Document', ['public', 'Document'])
    reg.register('public', 'Silva Root', ['public', 'Folder'])
    reg.register('public', 'Silva Ghost', ['public', 'Ghost'])
    reg.register('public', 'Silva Image', ['public', 'Image'])
    reg.register('public', 'Silva DemoObject', ['public', 'DemoObject'])
    reg.register('public', 'Silva File', ['public', 'File'])
    reg.register('public', 'Silva Indexer', ['public', 'Indexer'])
    reg.register('public', 'Silva SQL Data Source',
                 ['public', 'SQLDataSource'])

    # add
    reg.register('add', 'Silva Folder', ['add', 'Folder'])
    reg.register('add', 'Silva Publication', ['add', 'Publication'])
    reg.register('add', 'Silva Document', ['add', 'Document'])
    reg.register('add', 'Silva Ghost', ['add', 'Ghost'])
    reg.register('add', 'Silva Image', ['add', 'Image'])
    reg.register('add', 'Silva DemoObject', ['add', 'DemoObject'])
    reg.register('add', 'Silva File', ['add', 'File'])
    reg.register('add', 'Silva Indexer', ['add', 'Indexer'])
    reg.register('add', 'Silva SQL Data Source', ['add', 'SQLDataSource'])

def registerGroupsViews(reg):
    """Register groups views on registry.
    """
    reg.register(
        'edit', 'Silva Group', ['edit', 'Asset', 'Groups', 'Group'])
    reg.register(
        'edit', 'Silva Virtual Group', ['edit', 'Asset', 'Groups', 'VirtualGroup'])
    reg.register('add', 'Silva Group', ['add', 'Groups', 'Group'])
    reg.register('add', 'Silva Virtual Group', ['add', 'Groups', 'VirtualGroup'])

def unregisterViews(reg):
    for meta_type in ['Silva Folder', 'Silva Document',
                      'Silva Publication', 'Silva Ghost', 'Silva Image',
                      'Silva DemoObject', 'Silva File', 'Silva Indexer',
                      'Silva SQL Data Source', 'Silva Group', 
                      'Silva Virtual Group']:
        reg.unregister('edit', meta_type)
        reg.unregister('public', meta_type)
        reg.unregister('add', meta_type)
    reg.unregister('edit', 'Silva Root')
    reg.unregister('public', 'Silva Root')
    reg.unregister('edit', 'Silva Simple Member')
    # next line for hysterical reasons, should go away 
    reg.unregister('public', 'Silva Simple Member')

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the core widgets from the filesystem
    add_fss_directory_view(root, 'service_widgets', __file__, 'widgets')

    # create the editor service
    root.manage_addProduct['XMLWidgets'].manage_addEditorService(
        'service_editor')
    # create the services for XMLWidgets
    for name in ['service_doc_editor', 'service_doc_previewer',
                 'service_doc_viewer',
                 'service_field_editor', 'service_field_viewer',
                 'service_nlist_editor', 'service_nlist_previewer',
                 'service_nlist_viewer',
                 'service_sub_editor', 'service_sub_previewer',
                 'service_sub_viewer',
                 'service_table_editor', 'service_table_viewer']:
        root.manage_addProduct['XMLWidgets'].manage_addWidgetRegistry(name)

    # now register all widgets
    # XXX not really necessary; the "install" should take case of this
    registerCoreWidgets(root)
    
    
def registerCoreWidgets(root):
    """ register the core widgets at the corresponding registries.
    this function assumes the registries already exist.
    """
    registerDocEditor(root)
    registerDocPreviewer(root)
    registerDocViewer(root)
    registerFieldEditor(root)
    registerFieldViewer(root)
    registerNListEditor(root)
    registerNListPreviewer(root)
    registerNListViewer(root)
    registerSubEditor(root)
    registerSubPreviewer(root)
    registerSubViewer(root)
    registerTableEditor(root)
    registerTableViewer(root)

def registerDocEditor(root):
    wr = root.service_doc_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_normal'))

    for nodeName in ['p', 'heading', 'list', 'pre', 'toc', 'image', 'table',
                     'nlist', 'dlist', 'code', 'externaldata']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))

    wr.setDisplayName('doc', 'Title')
    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('pre', 'Preformatted')
    wr.setDisplayName('toc', 'Table of contents')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('table', 'Table')
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('dlist', 'Definition list')
    wr.setDisplayName('code', 'Code Element')
    wr.setDisplayName('externaldata', 'External Data')

    wr.setAllowed('doc', ['p', 'heading', 'list', 'dlist', 'pre', 'image', 
                  'table', 'nlist', 'toc', 'code', 'externaldata'])


def registerDocViewer(root):
    wr = root.service_doc_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'toc', 'image', 'nlist',
                 'table', 'dlist', 'code', 'externaldata']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))

def registerDocPreviewer(root):
    wr = root.service_doc_previewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'nlist', 'table',
                 'dlist', 'externaldata']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))

    wr.addWidget('toc', ('service_widgets', 'element', 'doc_elements',
                             'toc', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements',
                                'image', 'mode_preview'))
    wr.addWidget('code', ('service_widgets', 'element', 'doc_elements',
                               'code', 'mode_preview'))

def registerFieldEditor(root):
    wr = root.service_field_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_normal'))

    for nodeName in ['p', 'heading', 'list', 'image', 'nlist']:
        wr.addWidget(nodeName,
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))

    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('nlist', 'Complex list')

    wr.setAllowed('doc', ['p', 'heading', 'list', 'nlist', 'image'])

def registerFieldViewer(root):
    wr = root.service_field_viewer
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_view'))

    for name in ['p', 'list', 'heading', 'image', 'nlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                  name, 'mode_view'))

def registerNListEditor(root):
    wr = root.service_nlist_editor
    wr.clearWidgets()

    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_normal'))
    
    for nodeName in ['li']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'nlist_elements',
                           nodeName, 'mode_normal'))
        
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('li', 'List item')
    wr.setDisplayName('title', 'List title')
    
    wr.setAllowed('nlist', ['li'])
    
def registerNListPreviewer(root):
    wr = root.service_nlist_previewer
    wr.clearWidgets()

    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_view'))
    
    for name in ['li']:
        wr.addWidget(name, ('service_widgets', 'element', 'nlist_elements',
                                name, 'mode_view'))

def registerNListViewer(root):
    wr = root.service_nlist_viewer
    wr.clearWidgets()
    
    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_view'))
    
    for name in ['li']:
        wr.addWidget(name, ('service_widgets', 'element', 'nlist_elements',
                                 name, 'mode_view'))

def registerSubEditor(root):
    wr = root.service_sub_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_normal'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_normal'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_normal'))
    
    for nodeName in ['p', 'heading', 'list', 'image', 'nlist', 'pre', 'dlist']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'doc_elements',
                           nodeName, 'mode_normal'))
        
    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('pre', 'Preformatted')
    wr.setDisplayName('dlist', 'Definition list')

    for nodeName in ('doc', 'li', 'field'):
        wr.setAllowed(nodeName,  ['p', 'heading', 'list', 'nlist', 'image',
                                     'pre', 'dlist'])

def registerSubPreviewer(root):
    wr = root.service_sub_previewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'nlist', 'pre', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))
        
    # XX originally used mode_preview here, why?
    #wr.addWidget('image', ('service_widgets', 'element', 'doc_elements',
    #                           'image', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements',
                                'image', 'mode_view'))

def registerSubViewer(root):
    wr = root.service_sub_viewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'image', 'nlist', 'pre', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements',
                                 name, 'mode_view'))

def registerTableEditor(root):
    wr = root.service_table_editor
    wr.clearWidgets()
    
    wr.addWidget('table', ('service_widgets', 'top', 'table', 'mode_normal'))
    
    for nodeName in ['row', 'row_heading']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'table_elements',
                           nodeName, 'mode_normal'))

    # add a field that doesn't do any displaying, just for sub editor invocation
    wr.addWidget('field',
                 ('service_widgets', 'element', 'table_elements', 'field'))
    wr.setDisplayName('table', 'Table')
    wr.setDisplayName('row', 'Row')
    wr.setDisplayName('row_heading', 'Row heading')
    
    wr.setAllowed('table', ['row', 'row_heading'])

def registerTableViewer(root):
    wr = root.service_table_viewer
    wr.clearWidgets()
    
    wr.addWidget('table', ('service_widgets', 'top', 'table', 'mode_view'))
    
    for name in ['row', 'row_heading']:
        wr.addWidget(name, ('service_widgets', 'element', 'table_elements',
                                 name, 'mode_view'))

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
        # drop silva defined text indexes in deference to zctextindex
        # XXX: what does this do?? If a TextIndex is found in the indexes to
        # create, it is dropped from the catalog?? 
        if field_type in ('TextIndex',):
            catalog.delIndex(field_name)

        elif field_name in existing_indexes:
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

if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
