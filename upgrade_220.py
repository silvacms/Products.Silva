# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# zope
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import setSite

from Products.Five.site.interfaces import IFiveSiteManager
from Products.SilvaLayout.install import resetMetadata # Should be in Silva ?
import OFS.Image

# python
from cStringIO import StringIO

# silva imports
from Products.Silva.install import configureIntIds
from Products.Silva.interfaces import IVersionedContent, ISiteManager, IContainer
from Products.Silva.upgrade import BaseUpgrader,AnyMetaType
from Products.Silva.adapters import version_management
from Products.Silva.File import FileSystemFile
import zLOG


#-----------------------------------------------------------------------------
# 2.1.0 to 2.2.0a1
#-----------------------------------------------------------------------------

VERSION_A1='2.2a1'

class RootUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        # If it's a Five site manager disable it first.
        if ISite.providedBy(obj):
            sm = obj.getSiteManager()
            if IFiveSiteManager.providedBy(sm):
                from Products.Five.site.localsite import disableLocalSiteHook
                disableLocalSiteHook(obj)

        # Activate local site, add an intid service.
        ism = ISiteManager(obj)
        if not ism.isSite():
            ism.makeSite()
            setSite(obj)

        if not hasattr(obj, 'service_ids'):
            configureIntIds(obj)

        reg = obj.service_view_registry

        # Delete unused Silva Document service
        for s in ['service_doc_previewer', 'service_nlist_previewer','service_sub_previewer',]:
            if hasattr(obj, s):
                obj.manage_delObjects([s,])
        reg.unregister('public', 'Silva Document Version')
        reg.unregister('add', 'Silva Document')
        reg.unregister('preview', 'Silva Document Version')

        # Delete unused Silva views
        reg.unregister('public', 'Silva AutoTOC')

        # Clean SilvaLayout mess
        if hasattr(obj, "__silva_layout_installed__"):
            if 'silva-layout-vhost-root' in obj.service_metadata.getCollection().getMetadataSets():
                resetMetadata(obj, ['silva-layout-vhost-root'])
            reg.unregister('edit', 'LayoutConfiguration')
            reg.unregister('public', 'LayoutConfiguration')
            reg.unregister('add', 'LayoutConfiguration')
            if hasattr(obj.service_views, 'SilvaLayout'):
                obj.service_views.manage_delObjects(['SilvaLayout'])

        # Install ExternalSources, and setup cs_toc and cs_citation CS's.
        service_ext = obj.service_extensions
        if not service_ext.is_installed('SilvaExternalSources'):
            service_ext.install('SilvaExternalSources')
        if not hasattr(obj, 'cs_toc'):
            toc = obj.service_codesources.manage_copyObjects(['cs_toc',])
            obj.manage_pasteObjects(toc)
        if not hasattr(obj, 'cs_citation'):
            cit = obj.service_codesources.manage_copyObjects(['cs_citation',])
            obj.manage_pasteObjects(cit)

        # Update service_files settings
        service_files = obj.service_files
        if hasattr(service_files, '_filesystem_storage_enabled'):
            if service_files._filesystem_storage_enabled:
                service_files.storage = FileSystemFile
            delattr(service_files , '_filesystem_storage_enabled')

        # Refresh all products
        service_ext.refresh_all()
        return obj

RootUpgrader = RootUpgrader(VERSION_A1, 'Silva Root')


class ImagesUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        # Add stuff here
        data = None
        hires_image = obj.hires_image
        if hires_image is None:
            hires_image = obj.image
        if hires_image is None:
            # Can't do anything
            return obj
        if hires_image.meta_type == 'Image':
            data = StringIO(str(hires_image.data))
        elif hires_image.meta_type == 'ExtImage':
            filename = hires_image._get_fsname(hires_image.get_filename())
            data = open(filename, 'rb')
        elif hires_image.meta_type == 'Silva File':
            # Already converted ?
            return obj
        else:
            raise ValueError, "Unknown mimetype"
        full_data = data.read()
        data.seek(0)
        ct, _, _ = OFS.Image.getImageInfo(full_data)
        if not ct:
            raise ValueError, "Impossible to detect mimetype"
        obj._image_factory('hires_image', data, ct)
        obj._createDerivedImages()
        data.close()
        zLOG.LOG('Silva', zLOG.INFO,
                 "Image %s upgraded" % '/'.join(obj.getPhysicalPath()))
        return obj


ImagesUpgrader = ImagesUpgrader(VERSION_A1, 'Silva Image')


class SilvaXMLUpgrader(BaseUpgrader):
    '''Upgrades all SilvaXML (documents), converting
       <toc> elements to cs_toc sources and
       <citation> elements to cs_citation sources'''
    def upgrade(self, obj):
        if IVersionedContent.providedBy(obj):
            vm = version_management.getVersionManagementAdapter(obj)
            for version in vm.getVersions():
                if hasattr(version, 'content'):
                    dom = version.content
                    if hasattr(dom, 'documentElement'):
                        self._upgrade_tocs(obj, dom.documentElement)
                        self._upgrade_citations(obj, dom.documentElement)
        return obj

    def _upgrade_citations(self, obj, doc_el):
        cites = doc_el.getElementsByTagName('cite')
        if cites:
            zLOG.LOG(
                'Silva', zLOG.INFO,
                'Upgrading CITE Elements in: %s' % ('/'.join(obj.getPhysicalPath())))
        for c in cites:
            author = source = ''
            citation = []
            #html isn't currently allowed in author, source, so
            # we don't need to "sanity" check them!
            for node in c.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    if node.nodeName == 'author':
                        author = node.firstChild.writeStream().getvalue().replace('&lt;','<')
                    elif node.nodeName == 'source':
                        source = node.firstChild.writeStream().getvalue().replace('&lt;','<')
                    else:
                        citation.append(node.writeStream().getvalue().replace('&lt;','<'))
                else:
                    citation.append(node.writeStream().getvalue().replace('&lt;','<'))
            citation = ''.join(citation)

            cs = doc_el.createElement('source')
            cs.setAttribute('id','cs_citation')

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','source')
            p.appendChild(doc_el.createTextNode(source))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','author')
            p.appendChild(doc_el.createTextNode(author))
            cs.appendChild(p)

            p = doc_el.createElement('parameter')
            p.setAttribute('type','string')
            p.setAttribute('key','citation')
            p.appendChild(doc_el.createTextNode(citation))
            cs.appendChild(p)

            c.parentNode.replaceChild(cs,c)

    def _upgrade_tocs(self, obj, doc_el):
        tocs = doc_el.getElementsByTagName('toc')
        if tocs:
            zLOG.LOG(
                'Silva', zLOG.INFO,
                'Upgrading TOC Elements in: %s' % ('/'.join(obj.getPhysicalPath())))
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

SilvaXMLUpgrader = SilvaXMLUpgrader(VERSION_A1, AnyMetaType)


#-----------------------------------------------------------------------------
# 2.2.0a1 to 2.2.0a2
#-----------------------------------------------------------------------------

VERSION_A2='2.2a2'

class AllowedAddablesUpgrader(BaseUpgrader):

    def upgrade(self, obj):
        if IContainer.providedBy(obj):
            if hasattr(obj,'_addables_allowed_in_publication'):
                obj._addables_allowed_in_container = obj._addables_allowed_in_publication
                del obj._addables_allowed_in_publication
            elif not hasattr(obj, '_addables_allowed_in_container'):
                obj._addables_allowed_in_container = None
        return obj
AllowedAddablesUpgrader = AllowedAddablesUpgrader(VERSION_A2, AnyMetaType)
