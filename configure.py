"""Contains a fairly dumb setup system to configure the Silva root.
"""

from Products.FileSystemSite.DirectoryView import manage_addDirectoryView

def configure(root):
    configureProperties(root)
    configureCoreFolders(root)
    configureViews(root)
    configureXMLWidgets(root)
    
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
    manage_addDirectoryView(root, 'Products/Silva/globals', 'globals')
    # commonly used python scripts (XXX probably should go away)
    manage_addDirectoryView(root,
                            'Products/Silva/service_utils', 'service_utils')

def configureViews(root):
    """The view infrastructure for Silva.
    """
    # view registry
    root.manage_addProduct['Silva'].manage_addMultiViewRegistry(
        'service_view_registry')
    # folder contains the various view trees
    root.manage_addFolder('service_views')
    # create the core views from filesystem
    manage_addDirectoryView(root.service_views,
                            'Products/Silva/views', 'Silva')
    # also register views
    registerViews(root.service_view_registry)
    # and set Silva tree XXX should be more polite to extension packages
    root.service_view_registry.set_trees(['Silva'])
    
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

    # public
    reg.register('public', 'Silva Folder', ['public', 'Folder'])
    reg.register('public', 'Silva Publication', ['public', 'Folder'])
    reg.register('public', 'Silva Document', ['public', 'Document'])
    reg.register('public', 'Silva Root', ['public', 'Folder'])
    reg.register('public', 'Silva Ghost', ['public', 'Ghost'])
    reg.register('public', 'Silva Image', ['public', 'Image'])
    reg.register('public', 'Silva DemoObject', ['public', 'DemoObject'])
    reg.register('public', 'Silva File', ['public', 'File'])

    # add
    reg.register('add', 'Silva Folder', ['add', 'Folder'])
    reg.register('add', 'Silva Publication', ['add', 'Publication'])
    reg.register('add', 'Silva Document', ['add', 'Document'])
    reg.register('add', 'Silva Ghost', ['add', 'Ghost'])
    reg.register('add', 'Silva Image', ['add', 'Image'])
    reg.register('add', 'Silva DemoObject', ['add', 'DemoObject'])
    reg.register('add', 'Silva File', ['add', 'File'])

def configureXMLWidgets(root):
    """Configure XMLWidgets registries, editor, etc'
    """
    # create the core widgets from the filesystem
    manage_addDirectoryView(root,
                            'Products/Silva/widgets', 'service_widgets')

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

    for nodeName in ['p', 'heading', 'list', 'pre', 'toc', 'image', 'table', 'nlist', 'dlist']:
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
    
    wr.setAllowed('doc', ['p', 'heading', 'list', 'pre', 'nlist', 'table', 'image', 'toc', 'dlist'])

def registerDocViewer(root):
    wr = root.service_doc_viewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))

    for name in ['p', 'list', 'heading', 'pre', 'toc', 'image', 'nlist', 'table', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

def registerDocPreviewer(root):
    wr = root.service_doc_previewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'doc', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'pre', 'nlist', 'table', 'dlist']:
        wr.addWidget(name, ('service_widgets', 'element', 'doc_elements', name, 'mode_view'))

    wr.addWidget('toc', ('service_widgets', 'element', 'doc_elements', 'toc', 'mode_preview'))
    wr.addWidget('image', ('service_widgets', 'element', 'doc_elements', 'image', 'mode_preview'))

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
        
    # XXX title needs a dummy treatment; otherwise the top/invalidate_cache_helper rfs
    # when trying to invalidate the cache for the list <title> tag
    # this referenced widget does not need to exist as it is _never_ used
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
    
    for nodeName in ['p', 'heading', 'list', 'image', 'nlist']:
        wr.addWidget(nodeName, 
                     ('service_widgets', 'element', 'doc_elements', nodeName, 'mode_normal'))
        
    wr.setDisplayName('p', 'Paragraph')
    wr.setDisplayName('heading', 'Heading')
    wr.setDisplayName('list', 'List')
    wr.setDisplayName('image', 'Image')
    wr.setDisplayName('nlist', 'Complex list')
    
    wr.setAllowed('doc', ['p', 'heading', 'list', 'nlist', 'image'])
    wr.setAllowed('li', ['p', 'heading', 'list', 'nlist', 'image'])
    wr.setAllowed('field', ['p', 'heading', 'list', 'nlist', 'image'])

def registerSubPreviewer(root):
    wr = root.service_sub_previewer
    wr.clearWidgets()
    
    wr.addWidget('doc', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('li', ('service_widgets', 'top', 'sub', 'mode_view'))
    wr.addWidget('field', ('service_widgets', 'top', 'sub', 'mode_view'))
    
    for name in ['p', 'list', 'heading', 'nlist']:
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
    
    for name in ['p', 'list', 'heading', 'image', 'nlist']:
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
