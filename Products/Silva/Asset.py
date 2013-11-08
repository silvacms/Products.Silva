# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from five import grok

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS import SimpleItem

from Products.Silva import SilvaPermissions
from Products.Silva.SilvaObject import ViewableObject
from Products.Silva.QuotaObject import QuotaObject
from Products.Silva.Publishable import NonPublishable
from Products.Silva.mangle import Bytes

from silva.core.interfaces import IAsset
from silva.core.smi.content import IEditScreen
from silva.core.smi.content.metadata import ContentReferencedBy
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from zeam.form import silva as silvaforms

logger = logging.getLogger('silva.core')


class Asset(NonPublishable, ViewableObject, QuotaObject,
            SimpleItem.SimpleItem):
    grok.baseclass()
    grok.implements(IAsset)

    security = ClassSecurityInfo()

    # ACCESSORS

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'fulltext')
    def fulltext(self):
        fulltextlist = [self.id, self.get_title()]
        return fulltextlist

    def get_filename(self):
        raise NotImplementedError

    def get_file_size(self):
        raise NotImplementedError

    def get_mime_type(self):
        raise NotImplementedError

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'get_file_system_path')
    def get_file_system_path(self):
        """Return path of the file containing the data on the filesystem.
        """
        return None

    def get_quota_usage(self):
        try:
            return self.get_file_size()
        except (AttributeError, NotImplementedError):
            # Well, not all content respect its interface.
            path = '/'.join(self.getPhysicalPath())
            logger.error('Invalid asset %s - %s', path, str(self.__class__))
            return -1


InitializeClass(Asset)


class AssetEditTab(silvaforms.SMIComposedForm):
    """ Edit tab
    """
    grok.context(IAsset)
    grok.name('content')
    grok.require('silva.ChangeSilvaContent')
    grok.implements(IEditScreen)

    label = _('Edit')


class SMIAssetPortlet(silvaviews.Viewlet):
    grok.baseclass()
    grok.context(IAsset)
    grok.view(AssetEditTab)
    grok.viewletmanager(silvaforms.SMIFormPortlets)


class AssetSize(SMIAssetPortlet):
    """Report size of this asset.
    """
    grok.order(80)

    def update(self):
        self.size = Bytes(self.context.get_file_size())


class AssetPath(SMIAssetPortlet):
    """Give filesystem path to that asset.
    """
    grok.order(90)
    grok.require('zope2.ViewManagementScreens')

    def update(self):
        self.path = None
        path = self.context.get_file_system_path()
        if path is not None:
            self.path = path.replace('/', ' / ')


class AssetReferencedBy(ContentReferencedBy):
    grok.order(100)
    grok.context(IAsset)
    grok.view(AssetEditTab)
