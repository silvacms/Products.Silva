# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Python
from cStringIO import StringIO
import os.path
import re
import zipfile

from five import grok
from silva.core import interfaces
from zope import contenttype

# Silva
from Products.Silva.MimetypeRegistry import mimetypeRegistry
from Products.Silva import mangle


class ZipFileImporter(grok.Adapter):
    """ Adapter for container-like objects to facilitate
    the import of archive files (e.g. zipfiles) and create
    Assets out of its contents and, optionally, to recreate
    the 'directory' structure contained in the archive file.
    """
    grok.implements(interfaces.IArchiveFileImporter)
    grok.provides(interfaces.IArchiveFileImporter)
    grok.context(interfaces.IContainer)

    def importArchive(self, archive, assettitle='', recreatedirs=1, replace=0):
        zip = zipfile.ZipFile(archive)

        # Lists the names of the files in the archive which were
        # succesfully added (or, if something went wrong, list it in
        # failed_list).
        succeeded_list = []
        failed_list = []

        # Extract filenames, not directories.
        for name in zip.namelist():
            path, filename = os.path.split(name)
            if not filename:
                # Its a directory entry
                continue

            if (re.match("^__MACOSX", path) or
                re.match(".*\.DS_Store$", filename)):
                # It's meta information from a Mac archive, and we
                # don't need it
                continue

            if recreatedirs and path:
                dirs = path.split('/')
                container = self._getSilvaContainer(
                    self.context, dirs, replace)
                if container is None:
                    failed_list.append('/'.join(dirs))
                    # Creating the folder failed - bailout for this
                    # zipped file...
                    continue
            else:
                filename = name
                container = self.context

            # Actually add object...
            mimetype, enc = contenttype.guess_content_type(name)
            factory = mimetypeRegistry.get(mimetype)

            extracted_file = StringIO(zip.read(name))
            id = self._makeId(filename, container, extracted_file, replace)
            added_object = factory(
                container, id, assettitle, extracted_file)
            if added_object is None:
                # Factories return None upon failure.
                # FIXME: can I extract some info for the reason of failure?
                failed_list.append(name)
            else:
                succeeded_list.append(name)

        return succeeded_list, failed_list

    def _makeId(self, filename, container, extracted_file, replace):
        if replace:
            id = filename
            if id in container.objectIds():
                container.manage_delObjects([id])
        else:
            id = self._getUniqueId(
                container, filename, file=extracted_file,
                interface=interfaces.IAsset)
        return id

    def _getSilvaContainer(self, context, path, replace=0):
        container = context
        for id in path:
            if replace and id in container.objectIds():
                container = container._getOb(id)
            else:
                container = self._addSilvaContainer(container, id)
        return container

    def _addSilvaContainer(self, context, id):
        idObj = mangle.Id(
            context, id, interface=interfaces.IContainer, allow_dup=1)
        if not idObj.isValid():
            return None

        while id in context.objectIds():
            obj = context[id]
            if interfaces.IContainer.providedBy(obj):
                return obj
            id = str(idObj.new())
        context.manage_addProduct['Silva'].manage_addFolder(id, id)
        return context[id]

    def _getUniqueId(self, context, suggestion, **kw):
        # Make filename valid and unique.
        id = mangle.Id(context, suggestion, **kw)
        id.cook().unique()
        return str(id)

