"""Install for Silva Core
"""

from Globals import package_home
import os

from Products.FileSystemSite.DirectoryView import manage_addDirectoryView
from Products.FileSystemSite.utils import minimalpath, expandpath

def add_fss_directory_view(obj, name, base, *args):
    """ add a FSS-DirectoryView object with lots of sanity checks.
    
    obj         where the new directory-object will be accessible
    name        name of the new zope object
    base        dirname(base) is taken as the base for the following relative path
    *args       directory names which form the relative path to our content directory

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
    # create the core views from filesystem
    add_fss_directory_view(root.service_views, 'Silva', __file__, 'views')
    # also register views
    registerViews(root.service_view_registry)
    # also re-configure security (XXX should this happen?)
    configureSecurity(root)
    # and reconfigure xml widget registries
    # FIXME: should we check if the registries exist?
    # (for upgrading, and maybe to handle accidential deletion)
    registerCoreWidgets(root)
    
def uninstall(root):
    unregisterViews(root.service_view_registry)
    root.service_views.manage_delObjects(['Silva'])  

def is_installed(root):
    return hasattr(root.service_views, 'Silva')

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
        ('help_url', '/silva/globals/help', 'string'),
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

def configureViews(root):
    """The view infrastructure for Silva.
    """
    # view registry
    root.manage_addProduct['Silva'].manage_addMultiViewRegistry(
        'service_view_registry')
    root.manage_addProduct['Silva'].manage_addExtensionService(
        'service_extensions')
    # folder contains the various view trees
    root.manage_addFolder('service_views')
    # and set Silva tree XXX should be more polite to extension packages
    root.service_view_registry.set_trees(['Silva'])

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
        'Add Silva SQL Data Sources',
        ]
    
    for add_permission in add_permissions:
        root.manage_permission(add_permission, all_author)

    # everybody may view root by default XXX (is this bad in case of upgrade/refresh)
    root.manage_permission('View',
                           all_reader + ['Anonymous', 'Authenticated', 'Viewer'])
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
    
def configureLayout(root, default=0):
    """Install layout code into root.
    If the default argument is true, ids will be prefixed with default_.
    """
    for id in ['layout_macro.html', 'content.html', 'rename-to-override.html',
               'standard_error_message', 'standard_unauthorized_message', ]:
        add_helper(root, id, globals(), zpt_add_helper, default)    

    for id in ['index_html.py', 'index_html_restricted.py', 'preview_html.py']:
        add_helper(root, id, globals(), py_add_helper, default)
       
    add_helper(root, 'frontend.css', globals(), dtml_add_helper, default)

# helpers to add various objects to the root from the layout directory
# these won't add FS objects but genuine ZMI managed code
def add_helper(root, id, info, add_func, default=0):
    filename = id
    if default:
        id = 'default_' + id
    text = read_file(filename, info)
    add_func(root, id, text)

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
    id = os.path.splitext(id)[0]
    if hasattr(root.aq_base, id):
        getattr(root, id).write(text)
    else:
        root.manage_addProduct['PythonScripts'].manage_addPythonScript(id)
        getattr(root, id).write(text)

def read_file(id, info):
    filename = os.path.join(package_home(info), 'layout', id)
    f = open(filename, 'rb')
    text = f.read()
    f.close()
    return text

def registerViews(reg):
    """Register core views on registry.
    """
    # edit
    reg.register('edit', 'Silva Folder', ['edit', 'Container', 'Folder'])
    reg.register('edit', 'Silva Document', ['edit', 'VersionedContent', 'Document'])
    reg.register('edit', 'Silva Root', ['edit', 'Container', 'Publication'])
    reg.register('edit', 'Silva Publication', ['edit', 'Container', 'Publication'])
    reg.register('edit', 'Silva Ghost', ['edit', 'VersionedContent', 'Ghost'])
    reg.register('edit', 'Silva Image', ['edit', 'Asset', 'Image'])
    reg.register('edit', 'Silva DemoObject', ['edit', 'VersionedContent', 'DemoObject'])
    reg.register('edit', 'Silva File', ['edit', 'Asset', 'File'])
    reg.register('edit', 'Silva Indexer', ['edit', 'Content', 'Indexer'])
    reg.register('edit', 'Silva SQL Data Source', ['edit', 'Asset', 'SQLDataSource'])
    
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

def unregisterViews(reg):
    for meta_type in ['Silva Folder', 'Silva Document',
                      'Silva Publication', 'Silva Ghost', 'Silva Image',
                      'Silva DemoObject', 'Silva File', 'Silva Indexer',
                      'Silva SQL Data Source',]:
        reg.unregister('edit', meta_type)
        reg.unregister('public', meta_type)
        reg.unregister('add', meta_type)
    reg.unregister('edit', 'Silva Root')
    reg.unregister('public', 'Silva Root')
    
def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the core widgets from the filesystem
    add_fss_directory_view(root, 'service_widgets', __file__, 'widgets')

    # create the editor service
    root.manage_addProduct['XMLWidgets'].manage_addEditorService(
        'service_editor')
    # create the services for XMLWidgets
    for name in ['service_doc_editor', 'service_doc_previewer', 'service_doc_viewer',
                 'service_field_editor', 'service_field_viewer',
                 'service_nlist_editor', 'service_nlist_previewer', 'service_nlist_viewer',
                 'service_sub_editor', 'service_sub_previewer', 'service_sub_viewer',
                 'service_table_editor', 'service_table_viewer']:
        root.manage_addProduct['XMLWidgets'].manage_addWidgetRegistry(name)

    # now register all widgets
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
                     ('service_widgets', 'element', 'doc_elements', nodeName, 'mode_normal'))

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
    
    wr.setAllowed('doc', ['p', 'heading', 'list', 'pre', 'nlist', 'table', 
                  'image', 'toc', 'dlist', 'code', 'externaldata'])


def registerDocViewer(root):
    wr = root.service_doc_viewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'toc', 'image', 'nlist', 
                 'table', 'dlist', 'code', 'externaldata']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

def registerDocPreviewer(root):
    wr = root.service_doc_previewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'pre', 'nlist', 'table', 'dlist', 'externaldata']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

    wr.addWidget('toc', ('service_widgets', 'element', 'doc_elements', 'toc', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements', 'image', 'mode_preview'))
    wr.addWidget('code', ('service_widgets', 'element', 'doc_elements', 'code', 'mode_preview'))

def registerFieldEditor(root):
    wr = root.service_field_editor
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'field', 'mode_normal'))
    
    for nodeName in ['p', 'heading', 'list', 'image', 'nlist']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'doc_elements', nodeName, 'mode_normal'))

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
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

def registerNListEditor(root):
    wr = root.service_nlist_editor
    wr.clearWidgets()
    
    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_normal'))
    
    for nodeName in ['li']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'nlist_elements', nodeName, 'mode_normal'))
        
    # XXX title needs a dummy treatment; otherwise the top/invalidate_cache_helper barfs
    # when trying to invalidate the cache for the list <title> tag
    # the referenced widget does not need to exist as it is _never_ used
    wr.addWidget('title',  ('service_widgets', 'dummy') )

    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('li', 'List item')
    wr.setDisplayName('title', 'List title')
    
    wr.setAllowed('nlist', ['li'])
    
def registerNListPreviewer(root):
    wr = root.service_nlist_previewer
    wr.clearWidgets()

    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_view'))
    
    for name in ['li']:
        wr.addWidget(name, ('service_widgets', 'element', 'nlist_elements', name, 'mode_view'))

def registerNListViewer(root):
    wr = root.service_nlist_viewer
    wr.clearWidgets()
    
    wr.addWidget('nlist', ('service_widgets', 'top', 'nlist', 'mode_view'))
    
    for name in ['li']:
        wr.addWidget(name, ('service_widgets', 'element', 'nlist_elements', name, 'mode_view'))

def registerSubEditor(root):
    wr = root.service_sub_editor
    wr.clearWidgets()

    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_normal'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_normal'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_normal'))
    
    for nodeName in ['p', 'heading', 'list', 'image', 'nlist', 'pre', 'dlist']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'doc_elements', nodeName, 'mode_normal'))
        
    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('nlist', 'Complex list')
    wr.setDisplayName('pre', 'Preformatted')
    wr.setDisplayName('dlist', 'Definition list')

    for nodeName in ('doc', 'li', 'field'):
        wr.setAllowed(nodeName,  ['p', 'heading', 'list', 'nlist', 'image', 'pre', 'dlist'])

def registerSubPreviewer(root):
    wr = root.service_sub_previewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'nlist', 'pre', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))
        
    # why mode_preview??
    #wr.addWidget('image', ('service_widgets', 'element', 'doc_elements', 'image', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements', 'image', 'mode_view'))

def registerSubViewer(root):
    wr = root.service_sub_viewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'image', 'nlist', 'pre', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

def registerTableEditor(root):
    wr = root.service_table_editor
    wr.clearWidgets()
    
    wr.addWidget('table', ('service_widgets', 'top', 'table', 'mode_normal'))
    
    for nodeName in ['row', 'row_heading']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'table_elements', nodeName, 'mode_normal'))
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
        wr.addWidget(name, ('service_widgets', 'element', 'table_elements', name, 'mode_view'))

if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
