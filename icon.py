# Copyright (c) 2003, 2004 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: icon.py,v 1.5.52.2 2004/04/01 16:29:45 guido Exp $

"""Sivla icon registry"""

# python
import os

# zope
import Globals
import OFS.misc_

# Silva
from Products.Silva.interfaces import IIcon, IFile, ISilvaObject
from Products.Silva.interfaces import IGhostContent, IGhostFolder

class RegistryError(Exception):
    """thrown on any error in registry"""

class _IconRegistry:

    def __init__(self):
        self._icon_mapping = {}
    
    def getIcon(self, object):
        if IGhostContent.isImplementedBy(object):
            version = object.getLastVersion()
            if version.get_link_status() == version.LINK_OK:
                kind = 'link_ok'
            else:
                kind = 'link_broken'
            identifier = ('ghost', kind)
        elif IGhostFolder.isImplementedBy(object):
            if object.get_link_status() == object.LINK_OK:
                if object.implements_publication():
                    kind = 'publication'
                else:
                    kind = 'folder'
            else:
                kind = 'link_broken'
            identifier = ('ghostfolder', kind)      
        elif IFile.isImplementedBy(object):
            identifier = ('mime_type', object.get_mime_type())
        elif ISilvaObject.isImplementedBy(object):
            identifier = ('meta_type', object.meta_type)
        else:
            try:
                # if this call gets an object rather then a class as
                # argument it will raise an AttributeError on __hash__
                ISilvaObject.isImplementedByInstancesOf(object)
            except AttributeError:
                raise RegistryError, "Icon not found"
            else:
                identifier = ('meta_type', object.meta_type)
        return self.getIconByIdentifier(identifier)

    def getIconByIdentifier(self, identifier):
        icon = self._icon_mapping.get(identifier, None)
        if icon is None:
            raise RegistryError, "No icon for %r" % (identifier, )
        return icon

    def registerIcon(self, identifier, icon, context):
        """register icon

            identifier: icon identifier as returned from getIconIdentifier()
            icon: path to icon (i.e. 'www/root.png')
            context: module context of icon (i.e. globals())

            raises  RegistryError if product doesn't exist
            NOTE: this will overwrite previous icon declarations
        """
        # NOTE: code copied from App.ProductContext, modified though
        product = self._get_module_from_context(context)
        name = os.path.split(icon)[1]
        icon = Globals.ImageFile(icon, context)
        icon.__roles__ = None
        if not hasattr(OFS.misc_.misc_, product):
            raise RegistryError, "The product %r doesn't exist" % product
        getattr(OFS.misc_.misc_, product)[name] = icon
        self._icon_mapping[identifier] = 'misc_/%s/%s' % (product, name)
            
    def _get_module_from_context(self, context):
        name = context['__name__']
        name_parts = name.split('.')
        if name.startswith('Products.'):
            return name_parts[1]
        return name_parts[0]

registry = _IconRegistry()

