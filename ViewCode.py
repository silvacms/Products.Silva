from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Acquisition import aq_base

from Products.Silva import SilvaPermissions
from Products.Silva import mangle, icon


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
        if not self.REQUEST['AUTHENTICATED_USER'].has_permission(
                    SilvaPermissions.ChangeSilvaContent, target):
            tab = 'tab_preview'

        return '%s/edit/%s' % (target.absolute_url(), tab)
   
    security.declareProtected(SilvaPermissions.AccessContentsInformation,
                              'render_icon')
    def render_icon(self, obj=None, meta_type='Unknown'):
        """Gets the icon for the object and wraps that in an image tag"""
        tag = ('<img src="%(icon_path)s" width="16" height="16" border="0" '
                'alt="%(alt)s" />')
        icon_path = '%s/globals/silvageneric.gif' % self.get_root_url()
        if obj is not None:
            try:
                icon_path = icon.registry.getIcon(obj)
            except icon.RegistryError:
                icon_path = getattr(aq_base(obj), 'icon', icon_path)
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

        if self.implements_versioning():
            next_status = self.get_next_version_status()
            public = self.get_public_version_status()

            if next_status == 'no_next_version':
                pass
            elif next_status == 'not_approved':
                status = 'draft'
            elif next_status == 'request_pending':
                status = 'pending'
            elif next_status == 'approved':
                status = 'approved'

            if public == 'published':
                public_status = 'published'               
            elif public == 'closed':
                public_status = 'closed'

            if not status: 
                status_style = public_status.lower()
                status = 'none'
            else:
                status_style = status.lower()

        return (status, status_style, public_status)

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
    
InitializeClass(ViewCode)
