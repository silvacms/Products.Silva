# Copyright (c) 2002-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$
import os

# Zope 2
from Acquisition import aq_base
from DateTime import DateTime
from OFS import Image

# Silva
from silva.core.interfaces import IRoot
from silva.core.services.interfaces import ICataloging

from Products.Silva.tocfilter import TOCFilterService
from Products.Silva import roleinfo
from Products.Silva import MAILDROPHOST_AVAILABLE, MAILHOST_ID
from Products.Silva.ExtensionRegistry import extensionRegistry


def installFromScratch(root):
    configureSecurity(root)
    root.manage_addProduct['Silva'].manage_addExtensionService(
        'service_extensions', 'Silva Product and Extension Configuration')
    # now do the uinstallable stuff (views)
    install(root)
    setInitialSkin(root, 'Standard Issue')
    installSilvaExternalSources(root)
    installSilvaDocument(root)
    installSilvaFind(root)


# silva core install/uninstall are really only used at one go in refresh
def install(root):
    # add or update service metadata and catalog
    configureMetadata(root)

    # configure membership; this checks whether this is necessary
    configureMembership(root)
    # also re-configure security (XXX should this happen?)
    configureSecurity(root)

    # set up/refresh some mandatory services
    configureServices(root)


def uninstall(root):
    pass


def is_installed(root):
    return IRoot.providedBy(root)


def configureMetadata(root):
    installed_ids = root.objectIds()
    # See if catalog exists, if not create one
    if not 'service_catalog' in installed_ids:
        factory = root.manage_addProduct['silva.core.services']
        factory.manage_addCatalogService('service_catalog')

    # Install metadata
    if not 'service_metadata' in installed_ids:
        factory = root.manage_addProduct['SilvaMetadata']
        factory.manage_addMetadataTool('service_metadata')

    # load up the default metadata
    silva_docs = os.path.join(os.path.dirname(__file__), 'doc')

    metadata_sets_types = [
        (('silva-content', 'silva-extra'),
         ('Silva Folder', 'Silva File', 'Silva Image', 'Silva Root',
          'Silva Publication', 'Silva Indexer', 'Silva AutoTOC',
          'Silva Link Version')),
        (('silva-layout',),
         ('Silva Root', 'Silva Publication'))]

    collection = root.service_metadata.getCollection()
    ids = collection.objectIds()
    for metadata_sets, types in metadata_sets_types:
        for metadata_set in metadata_sets:
            if metadata_set in ids:
                collection.manage_delObjects([metadata_set])
            xml_file = os.path.join(silva_docs, "%s.xml" % metadata_set)
            with open(xml_file, 'r') as fh:
                collection.importSet(fh)
        root.service_metadata.addTypesMapping(types, metadata_sets)

    types = ('Silva Ghost Folder', 'Silva Ghost Version')
    root.service_metadata.addTypesMapping(types, ('', ))
    root.service_metadata.initializeMetadata()

    # Reindex the Silva root
    ICataloging(root).reindex()


def configureServices(root):
    """Set up required Services
    """
    factory = root.manage_addProduct['Silva']
    installed_ids = root.objectIds()

    # service files
    if 'service_files' not in installed_ids:
        factory.manage_addFilesService('service_files')

    # service message
    if 'service_messages' not in installed_ids:
        factory.manage_addEmailMessageService()

    # service container policy
    if 'service_containerpolicy' not in installed_ids:
        factory.manage_addContainerPolicyRegistry()

        # XXX Should move in a event service added
        from Products.Silva.AutoTOC import AutoTOCPolicy
        root.service_containerpolicy.register(
            'Silva AutoTOC', AutoTOCPolicy, 0)

    # service references
    factory = root.manage_addProduct['silva.core.references']
    if 'service_references' not in installed_ids:
        factory.manage_addReferenceService('service_references')

    # service toc filter
    if 'service_toc_filter' not in installed_ids:
        filter_service = TOCFilterService()
        root._setObject(filter_service.id, filter_service)

    # setup mailhost
    if not MAILHOST_ID in root.objectIds():
        if MAILDROPHOST_AVAILABLE:
            factory = root.manage_addProduct['MaildropHost']
            factory.manage_addMaildropHost(
                MAILHOST_ID, 'Spool based mail delivery')
        else:
            factory = root.manage_addProduct['MailHost']
            factory.manage_addMailHost(
                MAILHOST_ID, 'Mail Delivery Service')


def configureSecurity(root):
    """Update the security tab settings to the Silva defaults.
    """
    # add the appropriate roles if necessary
    userdefined_roles = root.userdefined_roles()

    app = root.getPhysicalRoot()
    roles = set(userdefined_roles).union(roleinfo.ASSIGNABLE_ROLES)
    app.__ac_roles__ = tuple(roles)

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
        'Add Silva AutoTOCs',
        ]

    for add_permission in add_permissions:
        root.manage_permission(add_permission, roleinfo.AUTHOR_ROLES)

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
    root.manage_permission('Manage Silva content', roleinfo.EDITOR_ROLES)
    root.manage_permission('Manage Silva content settings', roleinfo.CHIEF_ROLES)
    root.manage_permission('Change Silva content', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Delete objects', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Manage properties', roleinfo.AUTHOR_ROLES)
    root.manage_permission('Read Silva content', roleinfo.READER_ROLES)


def configureMembership(root):
    """Install membership code into root.
    """
    # add member service and message service
    installed_ids = root.objectIds()
    factory = root.manage_addProduct['Silva']
    if 'service_members' not in installed_ids:
        if extensionRegistry.have('silva.pas.base'):
            root.service_extensions.install('silva.pas.base')
        else:
            factory.manage_addSimpleMemberService()

    if 'Members' not in installed_ids:
        root.manage_addProduct['BTreeFolder2'].manage_addBTreeFolder('Members')

# helpers to add various objects to the root from the layout directory
# these won't add FS objects but genuine ZMI managed code
def add_helper(root, id, info, add_func, default_if_existent=0, folder='layout', keep_extension=False):
    filename = id
    if (add_func == py_add_helper or add_func == pt_add_helper) and not keep_extension:
        id = os.path.splitext(id)[0]
    if default_if_existent and hasattr(root.aq_base, id):
        id = 'default_' + id
    text = read_file(filename, info, folder)
    text = text.replace('{__silva_version__}', 'Silva %s' % root.get_silva_software_version())
    add_func(root, id, text)

def pt_add_helper(root, id, text):
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

def fileobject_add_helper(context, id, text):
    if hasattr(context.aq_base, id):
        getattr(context, id).update_data(text)
    else:
        Image.manage_addFile(context, id, text, content_type='text/plain')


def read_file(id, info, folder):
    filename = os.path.join(os.path.dirname(info['__file__']), folder, id)
    f = open(filename, 'rb')
    try:
        return f.read()
    finally:
        f.close()


def installSilvaDocument(root):
    """Install SilvaDocument
    """
    if extensionRegistry.have('silva.app.document'):
        root.service_extensions.install('silva.app.document')
        if not hasattr(aq_base(root), 'index'):
            root.manage_addProduct['silva.app.document'].manage_addDocument('index', 'Welcome to Silva!')
            document = root.index
            version = document.get_editable()
            version.body.save_raw_text('<div><h1>Welcome to Silva!</h1><p>Welcome to Silva! This is the public view. To actually see something interesting, try adding \'/edit\' to your url (if you\'re not already editing, you can <a href="edit">click this link</a>).</p>')
            document.set_unapproved_version_publication_datetime(DateTime())
            document.approve_version()


def installSilvaExternalSources(root):
    """Install SilvaExternalSources
    """
    if extensionRegistry.have('SilvaExternalSources'):
        root.service_extensions.install('SilvaExternalSources')


def installSilvaFind(root):
    """Install SilvaFind
    """
    if extensionRegistry.have('SilvaFind'):
        root.service_extensions.install('SilvaFind')


def setInitialSkin(silvaroot, default_skinid):
    setid = 'silva-layout'
    metadataservice = silvaroot.service_metadata
    currentskin = metadataservice.getMetadataValue(silvaroot, setid, 'skin')
    if not currentskin:
        binding = metadataservice.getMetadata(silvaroot)
        binding.setValues(setid, {'skin': default_skinid})


if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
