# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# zope
from zope.app.component.hooks import setSite

from Products.SilvaLayout.install import resetMetadata # Should be in Silva ?
import OFS.Image

# python
from cStringIO import StringIO

# silva imports
from Products.Silva.install import configureIntIds
from Products.Silva.interfaces import IVersionedContent, ISiteManager
from Products.Silva.upgrade import BaseUpgrader
from Products.Silva.adapters import version_management
import zLOG




#-----------------------------------------------------------------------------
# 2.1.0 to 2.2.0a1
#-----------------------------------------------------------------------------

VERSION='2.2a1'

class RootUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        # Activate local site, add an intid service.
        ISiteManager(obj).makeSite()
        setSite(obj)
        configureIntIds(obj)

        reg = obj.service_view_registry

        # Delete unused Silva Document service
        obj.manage_delObjects(['service_doc_previewer', 'service_nlist_previewer',])
        obj.manage_delObjects(['service_sub_previewer',])
        reg.unregister('public', 'Silva Document Version')
        reg.unregister('add', 'Silva Document')
        reg.unregister('preview', 'Silva Document Version')

        # Clean SilvaLayout mess
        if hasattr(obj, "__silva_layout_installed__"):
            resetMetadata(obj, ['silva-layout-vhost-root'])
            reg.unregister('edit', 'LayoutConfiguration')
            reg.unregister('public', 'LayoutConfiguration')
            reg.unregister('add', 'LayoutConfiguration')
            if hasattr(obj.service_views, 'SilvaLayout'):
                obj.service_views.manage_delObjects(['SilvaLayout'])

        # Install ExternalSources, and setup cs_toc CS.
        service_ext = obj.service_extension
        if not service_ext.is_installed('SilvaExternalSources'):
            service_ext.install('SilvaExternalSources')
        if not hasattr(obj, 'cs_toc'):
            toc = obj.service_codesources.manage_copyObjects(['cs_toc',])
            obj.manage_pasteObjects(toc)

        # Refresh all products
        service_ext.refresh_all()
        return obj

RootUpgrader = RootUpgrader(VERSION, 'Silva Root')


class ImagesUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        # Add stuff here
        data = None
        hires_image = obj.hires_image
        if hires_image.meta_type == 'Image':
            data = StringIO(str(hires_image.data))
        elif hires_image.meta_type == 'Ext Image':
            filename = hires_image._get_fsname(hires_image.get_filename())
            data = open(filename, 'rb')
        elif hires_image.meta_type == 'Silva File':
            # Already converted ?
            return obj
        else:
            raise ValueError, "Unknown mimetype"
        ct, _, _ = OFS.Image.getImageInfo(self.hires_image.get_content())
        if not ct:
            raise ValueError, "Impossible to detect mimetype"
        obj._image_factory('hires_image', data, ct)
        obj._createDerivedImages()
        data.close()
        zLOG.LOG(
            'Silva', zLOG.INFO, "Image %s migrated" % '/'.join(image.getPhysicalPath()))
        return obj


ImagesUpgraer = ImagesUpgrader(VERSION, 'Silva Image')


class TOCElementUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        zLOG.LOG(
            'Silva', zLOG.INFO,
            'Upgrading TOC Elements in: %s' % ('/'.join(obj.getPhysicalPath())))
        if IVersionedContent.providedBy(obj):
            vm = version_management.getVersionManagementAdapter(obj)
            for version in vm.getVersions():
                if hasattr(version, 'content'):
                    dom = version.content
                    if hasattr(dom, 'documentElement'):
                        self._upgrade_helper(obj, dom.documentElement)
        return obj

    def _upgrade_helper(self, obj, doc_el):
        tocs = doc_el.getElementsByTagName('toc')
        path = '/'.join(obj.get_container().getPhysicalPath())
        for t in tocs:
            depth = t.getAttribute('toc_depth')
            if not depth:
                depth = '0'

            cs = doc_el.createElement('source')
            cs.setAttribute('id','cs_toc')

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','paths')
            p.appendChild(doc_el.createTextNode(path))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','show_icon')
            p.appendChild(doc_el.createTextNode('0'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','list')
            p.setAttribute('key','toc_types')
            p.appendChild(doc_el.createTextNode("['Silva Document','Silva Folder','Silva Publication']"))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','css_class')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','sort_on')
            p.appendChild(doc_el.createTextNode('alpha'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','capsule_title')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','depth')
            p.appendChild(doc_el.createTextNode(depth))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','display_headings')
            p.appendChild(doc_el.createTextNode('1'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','alignment')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','css_style')
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','order')
            p.appendChild(doc_el.createTextNode('normal'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','link_headings')
            p.appendChild(doc_el.createTextNode('1'))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','boolean')
            p.setAttribute('key','show_desc')
            p.appendChild(doc_el.createTextNode('0'))
            cs.appendChild(p)

            t.parentNode.replaceChild(cs,t)


TOCElementUpgrader = TOCElementUpgrader(VERSION, 'Silva Document')
###also needed for news and agenda items
