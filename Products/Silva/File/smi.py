# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from five import grok
from zope import schema
from zope.interface import Interface

from Products.Silva.Asset import SMIAssetPortlet
from Products.Silva.Asset import AssetEditTab
from silva.core.interfaces import IFile
from silva.core.conf.interfaces import ITitledContent
from silva.core.conf import schema as silvaschema
from silva.translations import translate as _
from zeam.form import silva as silvaforms
from zeam.form.base import NO_VALUE

logger = logging.getLogger('silva.file')


class IFileAddFields(ITitledContent):
    file = silvaschema.Bytes(title=_(u"File"), required=True)


class FileAddForm(silvaforms.SMIAddForm):
    """Add form for a file.
    """
    grok.context(IFile)
    grok.name(u'Silva File')

    fields = silvaforms.Fields(IFileAddFields)
    fields['id'].required = False
    fields['id'].validateForInterface = IFile
    fields['title'].required = False
    fields['file'].fileNotSetLabel = _(
        u"Click the Upload button to select a file.")

    def _add(self, parent, data):
        default_id = data['id'] is not NO_VALUE and data['id'] or u''
        default_title = data['title'] is not NO_VALUE and data['title'] or u''
        factory = parent.manage_addProduct['Silva']
        return factory.manage_addFile(
            default_id, default_title, data['file'])


class FileEditForm(silvaforms.SMISubForm):
    """Edit file.
    """
    grok.context(IFile)
    grok.view(AssetEditTab)
    grok.order(10)

    label = _(u'Edit file content')
    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager

    fields = silvaforms.Fields(IFileAddFields).omit('id')
    fields['title'].required = False
    fields['file'].fileSetLabel = _(
        u"Click the Upload button to replace the current file with a new file.")
    actions  = silvaforms.Actions(
        silvaforms.CancelEditAction(),
        silvaforms.EditAction())


class IFileTextFields(Interface):
    text = schema.Text(
        title=_(u'Text content'),
        description=_(u'Text contained in the file'),
        required=True)


class FileTextEditForm(silvaforms.SMISubForm):
    """Edit content as a text file.
    """
    grok.context(IFile)
    grok.view(AssetEditTab)
    grok.order(20)

    label = _(u'Edit text content')
    ignoreContent = False
    dataManager = silvaforms.SilvaDataManager

    fields = silvaforms.Fields(IFileTextFields)
    actions  = silvaforms.Actions(
        silvaforms.CancelEditAction(),
        silvaforms.EditAction())

    def available(self):
        if self.context.is_text_editable():
            try:
                unicode(self.context.get_text())
                return True
            except (UnicodeDecodeError, TypeError):
                return False
        return False


class InfoPortlet(SMIAssetPortlet):
    grok.context(IFile)

    def update(self):
        self.filename = self.context.get_filename()
        self.download_url = self.context.get_download_url(
            preview=True, request=self.request)
        self.mime_type = self.context.get_mime_type()
        self.content_encoding = self.context.get_content_encoding()

