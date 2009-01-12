# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from Acquisition import aq_base

from Products.Silva import SilvaPermissions
from Products.Silva import mangle, icon

from Products.Silva.interfaces import IVersionedContent, IContent, IContainer

class ViewCode:
    """A mixin to expose view specific code to the pagetemplates

    The methods in this class were formerly Pythonscripts, but were
    moved to Product code to optimize Silva
    """
    security = ClassSecurityInfo()

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_editor_link')
    def get_editor_link(self, target):
        """Returns the link where a client goes to when he clicks an object in tab_edit
        """
        tab = 'tab_edit'

        if not getSecurityManager().getUser().has_permission(
            SilvaPermissions.ChangeSilvaContent, target):
            tab = 'tab_preview'

        return '%s/edit/%s' % (target.absolute_url(), tab)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'render_icon')
    def render_icon(self, obj=None, meta_type='Unknown'):
        """Gets the icon for the object and wraps that in an image tag
        """
        tag = ('<img src="%(icon_path)s" width="16" height="16" border="0" '
               'alt="%(alt)s" title="%(alt)s" />')
        if obj is None:
            icon_path = '%s/globals/silvageneric.gif' % self.REQUEST['BASE2']
            return tag % {'icon_path': icon_path, 'alt': meta_type}
        try:
            icon_path = '%s/%s' % (self.REQUEST['BASE1'],
                icon.registry.getIcon(obj))
            meta_type = obj.meta_type
        except icon.RegistryError:
            icon_path = getattr(aq_base(obj), 'icon', None)
            if icon_path is None:
                icon_path = '%s/globals/silvageneric.gif' % self.REQUEST['BASE2']
            meta_type = getattr(obj, 'meta_type')
        return tag % {'icon_path': icon_path, 'alt': meta_type}

    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_icon_by_meta_type')
    def render_icon_by_meta_type(self, meta_type):
        """Renders an icon by meta type"""
        instance = None
        if callable(self.all_meta_types):
            all = self.all_meta_types()
        else:
            all = self.all_meta_types
        for d in all:
            if d['name'] == meta_type:
                if d.has_key('instance'):
                    return self.render_icon(d['instance'])
        return self.render_icon(meta_type=meta_type)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_object_status')
    def get_object_status(self):
        status = public_status = None
        status_style = 'blacklink'

        # XXX i18n - how can we translate those strings?

        if self.implements_versioning():
            next_status = self.get_next_version_status()
            public = self.get_public_version_status()
            status_style = None

            if next_status == 'no_next_version':
                pass
            elif next_status == 'not_approved':
                status = 'draft'
                status_style = 'draft'
            elif next_status == 'request_pending':
                status = 'pending'
                status_style = 'pending'
            elif next_status == 'approved':
                status = 'approved'
                status_style = 'approved'

            if public == 'published':
                public_status = 'published'
                if not status_style:
                    status_style = 'published'
            elif public == 'closed':
                public_status = 'closed'
                if not status_style:
                    status_style = 'closed'

            if not status:
                status = 'none'

        return (status, status_style, public_status)

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_processed_items')
    def get_processed_items(self):
        default = self.get_default()
        if default is not None:
            publishables = [default]
            i = 0
        else:
            publishables = []
            i = 1
        publishables.extend(self.get_ordered_publishables())

        result = []
        render_icon = self.render_icon
        for item in publishables:
            status = item.get_object_status()
            modification_datetime = item.get_modification_datetime()
            is_editable = status[0] in ['draft', 'pending', 'approved']
            is_published = status[2] == 'published'
            is_approved = status[0] == 'approved'
            is_closed = status[2] == 'closed'
            is_versioned_content = IVersionedContent.providedBy(item)
            d = {
                'number': i,
                'item': item,
                'item_id': item.id,
                'title_editable': item.get_title_editable(),
                'meta_type': item.meta_type,
                'item_url': item.absolute_url(),
                'editor_link': self.get_editor_link(item),
                'status_style': status[1],
                'has_modification_time': modification_datetime,
                'modification_time': mangle.DateTime(modification_datetime).toShortStr(),
                'last_author': item.sec_get_last_author_info().fullname(),
                'is_default': item is default,
                'is_container': IContainer.providedBy(item),
                'is_versioned_content': is_versioned_content,
                'is_content': IContent.providedBy(item) and not is_versioned_content,
                'is_editable': is_editable,
                'is_published': is_published,
                'is_approved': is_approved,
                'is_closed': is_closed,
                'is_published_or_approved': is_published or is_approved,
                'rendered_icon': render_icon(item),
                }
            result.append(d)
            i += 1
        return result

    security.declareProtected(SilvaPermissions.ReadSilvaContent,
                              'get_processed_assets')
    def get_processed_assets(self):
        result = []
        render_icon = self.render_icon

        for asset in self.get_assets():
            title = asset.get_title()
            modification_datetime = asset.get_modification_datetime()
            d = {
                'asset_id': asset.id,
                'asset_url': asset.absolute_url(),
                'meta_type': asset.meta_type,
                'last_author': asset.sec_get_last_author_info().fullname(),
                'title': title,
                'editor_link': self.get_editor_link(asset),
                'rendered_icon': render_icon(asset),
                'has_modification_time': modification_datetime,
                'modification_time': mangle.DateTime(modification_datetime).toShortStr(),
                }
            if title:
                d['blacklink_class'] = 'blacklink'
            else:
                d['blacklink_class'] = 'closed'
            result.append(d)
        return result


    security.declareProtected(SilvaPermissions.ChangeSilvaContent, 'get_processed_status_tree')
    def get_processed_status_tree(self):
        tree = self.get_status_tree()
        ret = []
        for item in tree:
            obj = item[1]
            infodict = {}
            ret.append(infodict)

            infodict['indent'] = indent = item[0]
            infodict['id'] = mangle.String.truncate(obj.id, 22)

            # do not smash the smi because one object is broken
            if obj.meta_type[:6] == 'Broken':
                infodict['meta_type'] = obj.meta_type
                infodict['title_html'] = 'Broken content object'
                for key in ('absolute_url', 'icon', \
                            'implements_content', 'implements_container',
                            'implements_versioning'):
                    infodict[key]=''
                continue

            infodict['title'] = obj.get_title_editable()
            infodict['meta_type'] = obj.meta_type
            infodict['absolute_url'] = obj.absolute_url()
            infodict['icon'] = self.render_icon(obj)

            infodict['implements_content'] = obj.implements_content()
            if infodict['implements_content']:
                infodict['is_default'] = obj.is_default()
                infodict['container_meta_type'] = obj.get_container().meta_type

            infodict['implements_container'] = obj.implements_container()

            infodict['implements_versioning'] = obj.implements_versioning()
            if infodict['implements_versioning']:
                status, style, public_status = obj.get_object_status()
                infodict['status'] = status
                infodict['status_style'] = style
                infodict['public_status'] = public_status
                infodict['ref'] = self.create_ref(obj)

                datetime = obj.get_next_version_publication_datetime()
                if datetime:
                    str_datetime = mangle.DateTime(datetime).toShortStr()
                    infodict['next_version_publication_datetime'] = str_datetime

                datetime = obj.get_public_version_publication_datetime()
                if datetime:
                    str_datetime = mangle.DateTime(datetime).toDateStr()
                    infodict['public_version_publication_datetime'] = str_datetime

                datetime = obj.get_next_version_expiration_datetime()
                if datetime:
                    str_datetime = mangle.DateTime(datetime).toShortStr()
                    infodict['next_version_expiration_datetime'] = str_datetime

                datetime = obj.get_public_version_expiration_datetime()
                if datetime:
                    str_datetime = mangle.DateTime(datetime).toDateStr()
                    infodict['public_version_expiration_datetime'] = str_datetime
        return ret

    # this is a Python script that used to be located in the widgets dir of
    # SilvaDocument but had to be moved because of a change in Zope's
    # traversal machinery which made us have to switch from using
    # 'restrictedTraverse' to 'unrestrictedTraverse'
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                                'get_image')
    def get_image(self, image_context, image_path):
        """return an image object from a path"""
        image = image_context.unrestrictedTraverse(image_path, None)
        if image is None:
            return None
        # XXX checking for interface would be way nicer here...
        if getattr(image, 'meta_type', None) != 'Silva Image':
            image = None
        return image

InitializeClass(ViewCode)
