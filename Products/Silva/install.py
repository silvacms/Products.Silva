# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import os

# Zope 2
from OFS import Image

# Silva
from Products.SilvaMetadata.interfaces import IMetadataService
from five import grok
from silva.core.interfaces import IInstallRootEvent
from silva.core.interfaces import IInstalledServiceEvent
from silva.core.interfaces import IRoot, IPublication
from silva.core.services.interfaces import IContainerPolicyService

from Products.Silva import roleinfo
from Products.Silva import MAILDROPHOST_AVAILABLE, MAILHOST_ID
from Products.Silva.ExtensionRegistry import extensionRegistry


def install(root, extension):
    pass

def uninstall(root, extension):
    pass

def refresh(root, extension):
    # Refresh reinstall metadata.
    configure_metadata(root.service_metadata, None)
    configure_security(root, None)

def is_installed(root, extension):
    return IRoot.providedBy(root)


@grok.subscribe(IContainerPolicyService, IInstalledServiceEvent)
def configure_containerpolicy(service, event):
    from Products.Silva.AutoTOC import AutoTOCPolicy
    service.register('Silva AutoTOC', AutoTOCPolicy, 0)


@grok.subscribe(IMetadataService, IInstalledServiceEvent)
def configure_metadata(service, event):
    # load up the default metadata
    schema = os.path.join(os.path.dirname(__file__), 'schema')

    metadata_sets_types = [
        (('silva-content', 'silva-extra', 'silva-settings'),
         ('Silva Folder', 'Silva File', 'Silva Image', 'Silva Root',
          'Silva Publication', 'Silva Indexer', 'Silva AutoTOC',
          'Silva Link Version')),
        (('silva-layout',),
         ('Silva Root', 'Silva Publication'))]

    collection = service.getCollection()
    ids = collection.objectIds()
    for metadata_sets, types in metadata_sets_types:
        for metadata_set in metadata_sets:
            if metadata_set in ids:
                collection.manage_delObjects([metadata_set])
            xml_file = os.path.join(schema, "%s.xml" % metadata_set)
            with open(xml_file, 'r') as fh:
                collection.importSet(fh)
        service.addTypesMapping(types, metadata_sets)

    service.addTypesMapping(
        ('Silva Ghost Folder', 'Silva Ghost Version'),
        ('', ))

    if 'silva-quota' in ids:
        # If you reconfigure the site, refresh the silva-quota
        # metadata set if required.
        collection.manage_delObjects(['silva-quota'])
        xml_file = os.path.join(schema, 'silva-quota.xml')
        with open(xml_file, 'r') as fh:
            collection.importSet(fh)
        service.addTypesMapping(
            [c['name'] for c in extensionRegistry.get_contents(requires=[IPublication])],
            ('silva-quota',))

    service.initializeMetadata()

    # Set the default skin
    root = service.get_root()
    current_skin = service.getMetadataValue(root, 'silva-layout', 'skin')
    if not current_skin:
        binding = service.getMetadata(root)
        binding.setValues('silva-layout', {'skin': 'Standard Issue'})


@grok.subscribe(IRoot, IInstallRootEvent)
def install_mailhost(root, event):
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


@grok.subscribe(IRoot, IInstallRootEvent)
def configure_security(root, event):
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
        'Add Silva Ghost Assets',
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
    root.manage_permission('Manage Silva settings', roleinfo.MANAGER_ROLES)
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

if __name__ == '__main__':
    print """This module is not an installer. You don't have to run it."""
