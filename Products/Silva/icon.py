# -*- coding: utf-8 -*-
# Copyright (c) 2003-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import types

from five import grok
from zope.cachedescriptors.property import Lazy
from zope.publisher.interfaces.browser import IBrowserRequest

# Silva
from silva.core import interfaces
from silva.core.views.interfaces import IVirtualSite
from silva.core.interfaces.adapters import IIconResolver

_marker = object()

class IconDirectory(grok.DirectoryResource):
    # This export the globals directory containing all the default
    # icon using Grok.
    grok.path('icons')
    grok.name('silva.icons')


class Icon(object):
    """Define a simple icon, its value, how to compute its URL and
    render a tag.
    """
    grok.implements(interfaces.IIcon)
    template = """<img height="16" width="16" src="{url}" alt="{alt}" />"""

    def __init__(self, icon, template=None, url=None):
        self.icon = icon
        if url:
            self.get_url = types.MethodType(url, self)
        if template:
            self.template = template

    def get_url(self, resolver, content):
        return '/'.join((resolver.root_url, self.icon))

    def __str__(self):
        return str(self.icon)


class IconSprite(object):
    """Define an icon sprite that let you override the default icon
    set registered in Silva. You have the possibility to nest then in
    order to reuse customizations defined in an another sprites.
    """

    def __init__(self, sprite, template=None, url=None, parent=_marker):
        """
        ``sprite`` is a dictionnary containing the customized icon
               sub-url.
        ``template`` is a Python string used to create a tag if
               required.
        ``url`` is a method called if the URL of the icon is
               required. ``parent`` is the srpite that is extended.
        """
        if parent is _marker:
            parent = registry
        self._icons = {}
        self._parent = parent
        for key, icon in sprite.iteritems():
            if not isinstance(key, tuple):
                key = ('meta_type', key)
            if not interfaces.IIcon.providedBy(icon):
                icon = Icon(icon, template, url)
            self._icons[key] = icon

    def get(self, identifier, default=_marker):
        icon = self._icons.get(identifier)
        if icon is None:
            return self._parent.get(identifier, default)
        return icon


class IconRegistry(object):
    """The icon registry is the default icon sprite of Silva.
    """
    grok.implements(interfaces.IIconRegistry)

    def __init__(self):
        self._icons = {}

    def get(self, identifier, default=_marker):
        icon = self._icons.get(identifier, None)
        if icon is None:
            if default is _marker:
                raise ValueError(u"No icon for %r" % repr(identifier))
            return default
        return icon

    def register(self, identifier, icon):
        """Register an icon.
        """
        assert isinstance(identifier, tuple) and len(identifier) == 2, \
            'Invalid icon identifier'
        if not interfaces.IIcon.providedBy(icon):
            icon = Icon(icon)
        self._icons[identifier] = icon


@apply
def registry():
    """Create and initialize icon registry with Silva defaults.
    """
    registry = IconRegistry()

    mime_icons = [
        ('application/msword', 'file_doc.png'),
        ('application/pdf', 'file_pdf.png'),
        ('application/postscript', 'file_illustrator.png'),
        ('application/sdp', 'file_quicktime.png'),
        ('application/vnd.ms-excel', 'file_xls.png'),
        ('application/vnd.ms-powerpoint', 'file_ppt.png'),
        ('application/vnd.openxmlformats-officedocument.presentationml.presentation', 'file_ppt.png'),
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'file_xls.png'),
        ('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'file_doc.png'),
        ('application/x-javascript', 'file_js.png'),
        ('application/x-rtsp', 'file_quicktime.png'),
        ('application/x-sdp', 'file_quicktime.png'),
        ('application/x-zip-compressed', 'file_zip.png'),
        ('audio/aiff', 'file_aiff.png'),
        ('audio/basic', 'file_aiff.png'),
        ('audio/mid', 'file_aiff.png'),
        ('audio/midi', 'file_aiff.png'),
        ('audio/mp3', 'file_aiff.png'),
        ('audio/mp4', 'file_aiff.png'),
        ('audio/mpeg', 'file_aiff.png'),
        ('audio/mpeg3', 'file_aiff.png'),
        ('audio/wav', 'file_aiff.png'),
        ('audio/x-aiff', 'file_aiff.png'),
        ('audio/x-gsm', 'file_aiff.png'),
        ('audio/x-m4a', 'file_aiff.png'),
        ('audio/x-m4p', 'file_aiff.png'),
        ('audio/x-midi', 'file_aiff.png'),
        ('audio/x-mp3', 'file_aiff.png'),
        ('audio/x-mpeg', 'file_aiff.png'),
        ('audio/x-mpeg3', 'file_aiff.png'),
        ('audio/x-wav', 'file_aiff.png'),
        ('text/css', 'file_css.png'),
        ('text/html', 'file_html.png'),
        ('text/plain', 'file_txt.png'),
        ('text/xml', 'file_xml.png'),
        ('video/avi', 'file_quicktime.png'),
        ('video/mp4', 'file_quicktime.png'),
        ('video/mpeg', 'file_quicktime.png'),
        ('video/msvideo', 'file_quicktime.png'),
        ('video/quicktime', 'file_quicktime.png'),
        ('video/x-dv', 'file_quicktime.png'),
        ('video/x-mpeg', 'file_quicktime.png'),
        ('video/x-msvideo', 'file_quicktime.png'),
        ]
    for mimetype, icon_name in mime_icons:
        registry.register(
            ('mime_type', mimetype),
            '++static++/silva.icons/%s' % icon_name)

    misc_icons = [
        ('default', None, 'generic.png'),
        ('meta_type', None, 'missing.png'),
        ('meta_type', 'Silva Ghost Folder', 'ghost_folder.png'),
        ('meta_type', 'Silva Ghost Publication', 'ghost_publication.png'),
        ('meta_type', 'Broken Silva Ghost Folder', 'ghost_broken.png'),
        ('meta_type', 'Silva Ghost', 'ghost.png'),
        ('meta_type', 'Broken Silva Ghost', 'ghost_broken.png'),
    ]
    for cls, kind, icon_name in misc_icons:
        registry.register(
            (cls, kind),
            '++static++/silva.icons/%s' % icon_name)

    return registry


class IconResolver(grok.Adapter):
    """Resolve and return an icon.
    """
    grok.context(IBrowserRequest)
    grok.implements(IIconResolver)

    sprite = registry

    def __init__(self, request):
        self.request = request

    @Lazy
    def root_url(self):
        site = IVirtualSite(self.request)
        return site.get_root_url()

    def get_tag(self, content=None, identifier=None, default=_marker):
        if content is not None:
            icon = self.get_content(content)
            alt = getattr(content, 'meta_type', 'Missing')
        else:
            icon = self.get_identifier(identifier, default=_marker)
            alt = identifier or 'Missing'
        if icon is not None:
            return icon.template.format(
                url=icon.get_url(self, content), alt=alt)
        return u''

    def get_identifier(self, identifier, default=_marker):
        if not isinstance(identifier, tuple):
            identifier = ('meta_type', identifier)
        try:
            return self.sprite.get(identifier)
        except ValueError:
            if default is _marker:
                default = ('default', None)
            elif not isinstance(default, tuple):
                default = ('default', default)
            return self.sprite.get(default, default=None)

    def get_content(self, content):
        identifier = ('meta_type', None)
        default = ('default', None)
        try:
            if interfaces.IGhost.providedBy(content):
                viewable = content.get_viewable()
                if (viewable is not None and
                    viewable.get_link_status() is not None):
                    identifier = ('meta_type', 'Broken Silva Ghost')
                else:
                    identifier = ('meta_type', 'Silva Ghost')
            elif interfaces.IGhostFolder.providedBy(content):
                if content.get_link_status() is None:
                    if interfaces.IPublication.providedBy(content.get_haunted()):
                        identifier = ('meta_type', 'Silva Ghost Publication')
                    else:
                        identifier = ('meta_type', 'Silva Ghost Folder')
                else:
                    identifier = ('meta_type', 'Broken Silva Ghost Folder')
            elif interfaces.IFile.providedBy(content):
                identifier = ('mime_type', content.get_mime_type())
                default = ('meta_type', 'Silva File')
            elif interfaces.ISilvaObject.providedBy(content):
                identifier = ('meta_type', content.meta_type)
            elif content is None:
                default = ('meta_type', None)
            else:
                if interfaces.IAuthorization.providedBy(content):
                    content = content.source
                meta_type = getattr(content, 'meta_type', None)
                if meta_type is None:
                    raise ValueError(u"No icon for unknown object %r" % content)
                identifier = ('meta_type', meta_type)
            return self.sprite.get(identifier)
        except ValueError:
            return self.sprite.get(default, default=None)

    def get_content_url(self, content):
        """Return a content icon URL.
        """
        icon = self.get_content(content)
        if icon is not None:
            return icon.get_url(self, content)
        return None

    def get_identifier_url(self, identifier, default=_marker):
        """Return a URL out of a identifier.
        """
        icon = self.get_identifier(identifier, default=default)
        if icon is not None:
            return icon.get_url(self, None)
        return None
