# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

# Zope 3
from five import grok
from zope.app.schema.vocabulary import IVocabularyFactory
from zope.location.interfaces import ISite
from zope.schema.fieldproperty import FieldProperty
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.interface import directlyProvides

# Zope 2
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

# Silva
from Products.Silva.Image.content import ImageStorageConverter
from Products.Silva.File.content import BlobFile, ZODBFile
from silva.core import conf as silvaconf
from silva.core import interfaces
from silva.core.interfaces import ISilvaConfigurableService
from silva.core.services.base import SilvaService
from silva.core.services.interfaces import IFilesService
from silva.core.upgrade import upgrade
from silva.translations import translate as _
from zeam.form import silva as silvaforms

logger = logging.getLogger('silva.file')



def FileStorageTypeVocabulary(context):
    terms = [SimpleTerm(value=ZODBFile, title='ZODB File', token='ZODBFile'),
             SimpleTerm(value=BlobFile, title='Blob File', token='BlobFile'),]
    return SimpleVocabulary(terms)

directlyProvides(FileStorageTypeVocabulary, IVocabularyFactory)


class FilesService(SilvaService):
    meta_type = 'Silva Files Service'
    grok.implements(IFilesService, ISilvaConfigurableService)
    grok.name('service_files')
    silvaconf.default_service()
    silvaconf.icon('icons/service_files.png')

    security = ClassSecurityInfo()

    storage = FieldProperty(IFilesService['storage'])

    manage_options = (
        {'label':'Settings', 'action':'manage_settings'},
        ) + SilvaService.manage_options

    security.declarePrivate('new_file')
    def new_file(self, id):
        if self.storage is None:
            return ZODBFile(id)
        return self.storage(id)

    security.declarePrivate('upgrade_storage')
    def convert_storage(self, container):
        if self.storage is not None and self.storage is not ZODBFile:
            upg = upgrade.UpgradeRegistry()
            upg.register(
                StorageConverterHelper(container),
                '0.1', upgrade.AnyMetaType)
            upg.register(
                FileStorageConverter(self),
                '0.1', 'Silva File')
            upg.register(
                ImageStorageConverter(self),
                '0.1', 'Silva Image')
            upg.upgrade_tree(container, '0.1')

    def is_file_using_correct_storage(self, content):
        storage = ZODBFile
        if self.storage is not None:
            storage = self.storage
        return isinstance(content, storage)


InitializeClass(FilesService)


class FileServiceManagementView(silvaforms.ZMIComposedForm):
    """Edit File Service.
    """
    grok.require('zope2.ViewManagementScreens')
    grok.name('manage_settings')
    grok.context(FilesService)

    label = _(u"Configure file storage")


class FileServiceConfiguration(silvaforms.ComposedConfigurationForm):
    """Edit File Service.
    """
    grok.context(FilesService)

    label = _(u"Configure file storage")


class FileServiceSettings(silvaforms.ZMISubForm):
    grok.context(FilesService)
    grok.view(FileServiceManagementView)
    grok.order(10)

    label = _(u"Select storage")
    fields = silvaforms.Fields(IFilesService)
    actions = silvaforms.Actions(silvaforms.EditAction())
    ignoreContent = False


class FileServiceSettingsConfiguration(silvaforms.SMISubForm):
    grok.context(FilesService)
    silvaforms.view(FileServiceConfiguration)
    silvaforms.order(10)

    label = _(u"Select storage")
    fields = silvaforms.Fields(IFilesService)
    actions = silvaforms.Actions(
        silvaforms.CancelConfigurationAction(),
        silvaforms.EditAction())
    ignoreContent = False


class FileServiceConvert(silvaforms.ZMISubForm):
    grok.context(FilesService)
    grok.view(FileServiceManagementView)
    grok.order(20)

    label = _(u"Convert stored files")
    description = _(u"Convert all currently stored file to "
                    u"the current set storage.")

    def available(self):
        if self.context.storage is None:
            return False
        return self.context.storage is not ZODBFile

    @silvaforms.action(_(u'Convert all files'))
    def convert(self):
        parent = self.context.get_publication()
        self.context.convert_storage(parent)
        self.status = _(u'Storage for Silva Files and Images converted. '
                        u'Check the log for more details.')


class FileServiceConvertConfiguration(silvaforms.SMISubForm):
    grok.context(FilesService)
    grok.view(FileServiceConfiguration)
    grok.order(20)

    label = _(u"Convert stored files")
    description = _(u"Convert all currently stored file to "
                    u"the current set storage.")
    actions = silvaforms.Actions(silvaforms.CancelConfigurationAction())

    def available(self):
        if self.context.storage is None:
            return False
        return self.context.storage is not ZODBFile

    @silvaforms.action(_(u'Convert all files'))
    def convert(self):
        parent = self.context.get_publication()
        self.context.convert_storage(parent)
        self.send_message(
            _(u'Storage for Silva Files and Images converted. '
              u'Check the log for more details.'),
            type='feedback')


class StorageConverterHelper(object):
    """The purpose of this converter is to stop convertion if there is
    an another configuration.
    """
    grok.implements(interfaces.IUpgrader)

    def __init__(self, publication):
        self.startpoint = publication

    def validate(self, context):
        if context is self.startpoint:
            return False

        if ISite.providedBy(context):
            for obj in context.objectValues():
                if IFilesService.providedBy(obj):
                    raise StopIteration()
        return False

    def upgrade(self, context):
        return context


class FileStorageConverter(upgrade.BaseUpgrader):
    """Convert storage for a file.
    """
    grok.implements(interfaces.IUpgrader)

    def __init__(self, service):
        self.service = service

    def validate(self, content):
        if not interfaces.IFile.providedBy(content):
            return False
        if self.service.is_file_using_correct_storage(content):
            # don't convert that are already correct
            return False
        return True

    def upgrade(self, content):
        identifier = content.getId()

        tmp_identifier = identifier + 'conv_storage'
        new_file = self.service.new_file(identifier)
        container = content.aq_parent
        if not interfaces.IContainer.providedBy(container):
            # Self-autodestruct file.
            container._delObject(identifier)
            raise StopIteration
        container._setObject(tmp_identifier, new_file)
        new_file = container._getOb(tmp_identifier)
        self.replace_references(content, new_file)
        self.replace(content, new_file)
        new_file.set_file(
            content.get_file_fd(),
            content_type=content.get_content_type(),
            content_encoding=content.get_content_encoding())
        container._delObject(identifier)
        container.manage_renameObject(tmp_identifier, identifier)
        logger.info("File %s migrated" %
                    '/'.join(new_file.getPhysicalPath()))
        return new_file

