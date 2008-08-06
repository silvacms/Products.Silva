# Copyright (c) 2002-2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import string
import re
import os

# zope imports
import zLOG
from Globals import package_home

# silva imports
from Products.Silva.upgrade import BaseUpgrader, AnyMetaType
from Products.Silva.interfaces import ISilvaObject, IContainer, IVersionedContent
from Products.Silva.adapters.interfaces import IViewerSecurity
from Products.Silva.VersionedContent import VersionedContent
from Products.SilvaMetadata.Exceptions import BindingError
from Products.Silva import mangle

#-----------------------------------------------------------------------------
# 0.9.2 to 0.9.3
#-----------------------------------------------------------------------------

VERSION='0.9.3'

class MovedViewRegistry(BaseUpgrader):
    """handle view registry beeing moved out of the core"""

    def upgrade(self, root):
        svr = root.service_view_registry
        root._delObject('service_view_registry')
        root.manage_addProduct['SilvaViews'].manage_addMultiViewRegistry(
            'service_view_registry')
        #zLOG.LOG('Silva', zLOG.WARNING,
        #    'service_view_registry had to be recreated.\n'
        #    "Be sure to 'refresh all' your extensions.\n")
        return root

modelViewRegistery = MovedViewRegistry(VERSION, 'Silva Root', 50) 

class MovedDocument(BaseUpgrader):
    """handle moved silva document

        Silva Document was moved from core to a seperate package. This upgrader
        removes the objects in the silva root which were required by the
        core Silva Document.
    """

    def upgrade(self, root):
        root.manage_delObjects(['service_widgets', 'service_editor',
            'service_editorsupport',
            # xml widgets ahead
            'service_doc_editor', 'service_doc_previewer',
            'service_doc_viewer', 'service_field_editor',
            'service_field_viewer', 'service_nlist_editor',
            'service_nlist_previewer', 'service_nlist_viewer',
            'service_sub_editor', 'service_sub_previewer',
            'service_sub_viewer', 'service_table_editor',
            'service_table_viewer'])
        return root

movedDocument = MovedDocument(VERSION, 'Silva Root', 80)
            
class UpgradeAccessRestriction(BaseUpgrader):
    """upgrade access restrction

        access restriction by ip address was a proof of concept and has been
        replaced by IP groups.

        This upgrade does:

            XXX

    """

    ACCESS_RESTRICTION_PROPERTY = 'access_restriction'

    # match any quote _not_ preceeded by a backslash
    re_quote_split = re.compile(r'(?<![^\\]\\)"', re.M)

    # match any escapes of quotes (e.g. \\ or \" )
    re_drop_escape = re.compile(r'\\(\\|")')


    def upgrade(self, obj):
        if not hasattr(obj.aq_base, '_properties'):
            # if it is not a property manager it hardly can have access 
            # restrictions
            return obj
        if not obj.hasProperty(self.ACCESS_RESTRICTION_PROPERTY):
            # if it doesn't have the property nothing needs to be done
            return obj
        ar = self.parseAccessRestriction(obj).get('allowed_ip_addresses')
        at_text = getattr(obj, self.ACCESS_RESTRICTION_PROPERTY, '')
        log_text = []
        if ar:
            ar = [ s.upper() for s in ar ]
            if 'NONE' in ar:
                self._none_allowed(obj, ar)
            elif 'ALL' in ar:
                self._all_allowed(obj, ar)
            else:
                self._restrict(obj, ar)
        try:
            obj._delProperty(self.ACCESS_RESTRICTION_PROPERTY)
        except ValueError:
            pass
        return obj
        
    def _all_allowed(self, obj, ar):
        zLOG.LOG('Silva', zLOG.INFO, "Access restriction removed",
            "The access restriction of the object located at %s "
            "has been removed as it allowed ALL addresses access.\n" % (
                obj.absolute_url(), ))
                
    def _none_allowed(self, obj, ar):
        adapter = IViewerSecurity(obj)
        if adapter.getMinimumRole() == 'Anonymous':
            adapter.setMinimumRole('Viewer')
            zLOG.LOG('Silva', 'Access restriction removed',
                "The access restriction of the object located at %s "
                "has been removed. The object's 'access restriction by role' "
                "was set to 'viewer' as the access restriction did not allow "
                "any ip addresses access.\n" % obj.absolute_url())

    def _restrict(self, obj, ar):
        adapter = IViewerSecurity(obj)
        if adapter.getMinimumRole() == 'Anonymous':
            adapter.setMinimumRole('Viewer')
        ipg = self._createIPGroup(obj)
        for ip in ar:
            ipg.addIPRange(ip)
        self._assignRoleToGroup(obj, 'Viewer', ipg.getId())
        zLOG.LOG('Silva', zLOG.INFO, "Created IP Group %s" % ipg.getId(),
            "The ip based access restriction of the object located at %s"
            "was replaced by the newly created IP Group at %s.\n" % (
                obj.absolute_url(), ipg.absolute_url()))
        
    def _createIPGroup(self, context):
        if not IContainer.providedBy(context):
            context = context.aq_parent
        assert IContainer.providedBy(context)
        id = 'access_restriction_upgrade_group'
        id_template = id + '_%i'
        counter = 0
        while 1:
            if counter:
                id = id_template % counter
            try:
                context.manage_addProduct['Silva'].manage_addIPGroup(id,
                    'Automatically created IP Group', id)
            except ValueError:
                counter += 1
            except AttributeError:
                self._createGroupsService(context)
            else:
                break
        return context._getOb(id)

    def _assignRoleToGroup(self, obj, role, group_name):
        mapping = obj.sec_get_or_create_groupsmapping()
        mapping.assignRolesToGroup(group_name, [role])

    def _createGroupsService(self, context):
        try:
            groups = context.get_root().manage_addProduct['Groups']
        except AttributeError:
            raise AttributeError, "The Groups product is not installed. "\
                "Upgrading  your ip based access restrictions requires "\
                "IP Groups and a service_groups in your Silva root."
        zLOG.LOG('Silva', zLOG.INFO, 'Upgrade added service_groups',
            'service_groups added to Silva root located at %s\n' % (
                context.get_root().absolute_url(), ))
        groups.manage_addGroupsService('service_groups', '')

    ### ACCCESS RESTRICTION PARSER
    ### formerly found in helpers.py

    # This code is based on Clemens Klein-Robbenhaar's "CommentParser.py" 
    # Marc Petitmermet's and Wolfgang Korosec's code.
    #
    def parseAccessRestriction(self, obj):
        raw_string = ''
        raw_string = getattr(obj.aq_base, self.ACCESS_RESTRICTION_PROPERTY, '')
        if not raw_string:
            return {}
        return self._parse_raw(raw_string)

    #stupid record
    class State:
        pass

    def _parse_raw(self, raw_string):
        props = {}
        state = self.State()
        # first split due to quotes
        quoted = self.re_quote_split.split(raw_string)
        in_quote = None
        state.read_props = None
        for item in quoted:
            if in_quote:
                self._parse_quote(item, state, props)
            else:
                self._parse_unquote(item, state, props)
            in_quote = not in_quote
        return props


    def _parse_unquote(self, something, state, props):
        
        if not state.read_props:
            try:
                name, something = map (string.strip, something.split(':',1) )
            except ValueError:
                # no name: quit.
                return
            state.name = name
            props[name] = []
            state.plist = props[name]
            state.read_props = 1

        separate = something.split(';',1)
        if len(separate) > 1:
            something, rest = map (string.strip, separate)
        else:
            rest=None

        for p in map (string.strip, something.split(',') ):
            if p:
                state.plist.append(p)

        if rest is not None:
            state.read_props=None
            self._parse_unquote(rest, state, props)


    def _parse_quote(self, something, state, props):
        """ parse everything enclosed in quotes.
        this is an easy one: just remove the escapes
        """
        if not state.read_props:
            raise ValueError, "not inside a property definition: <<%s>>" % something

        something = self.re_drop_escape.sub(lambda match: match.group(1), something )
        state.plist.append(something)

upgradeAccessRestriction = UpgradeAccessRestriction(VERSION, AnyMetaType, 60)

class UpgradeTime(BaseUpgrader):

    def upgrade(self, obj):
        try:
            binding = obj.service_metadata.getMetadata(obj)
        except AttributeError:
            zLOG.LOG('Silva', zLOG.WARNING, "UpgradeTime failed on %r. "
                "Maybe a broken product?" % (obj, ))
            return obj
        except BindingError:
            return obj
        if binding is None:
            zLOG.LOG('Silva', zLOG.BLATHER,
                     'cannot upgrade meta data of '+obj.absolute_url())
            return obj
        mtime = getattr(obj, '_modification_datetime',
            obj.bobobase_modification_time())
        ctime = getattr(obj, '_creation_datetime', None)
        timings = {}
        for element, time in [
                ('creationtime', ctime),
                ('modificationtime', mtime) ]:
            old = binding.get('silva-extra', element_id=element)
            if old is None and time is not None:
                timings[element] = time
        binding.setValues('silva-extra', timings)
        return obj

upgradeTime = UpgradeTime(VERSION, AnyMetaType, 30)

class SimpleMetadataUpgrade(BaseUpgrader):
    """simple metadata upgrade, meaning: remove old set, add new set

        NOTE: this doesn't handle severe changes to the set, i.e. removing
        or renaming fields. Adding should be fine though.
    """

    def __init__(self, version, meta_type, name, filename):
        """constructor

            name: name in service_metadata
            filename: path to xml description of metadata set
        """
        super(SimpleMetadataUpgrade, self).__init__(version, meta_type)
        self.name = name
        self.filename = filename

    def upgrade(self, service_metadata):
        collection = service_metadata.getCollection()
        if self.name in collection.objectIds():
            collection.manage_delObjects([self.name])
        fh = open(self.filename, 'r')
        collection.importSet(fh)
        return service_metadata

xml_home = os.path.join(package_home(globals()), 'doc')
simpleMetadataUpgradeExtra = SimpleMetadataUpgrade(VERSION, 'Advanced Metadata Tool', 'silva-extra', os.path.join(xml_home, 'silva-extra.xml'))
simpleMetadataUpgradeContent = SimpleMetadataUpgrade(VERSION, 'Advanced Metadata Tool', 'silva-content', os.path.join(xml_home, 'silva-content.xml'))

class Reindex(BaseUpgrader):

    def upgrade(self, obj):
        if hasattr(obj.aq_base, 'reindex_object'):
            obj.reindex_object()
        return obj

reindex = Reindex(VERSION, AnyMetaType, 70)

class PublicRenderingCacheFlusher(BaseUpgrader):

    def upgrade(self, obj):
        if isinstance(obj, VersionedContent):
            obj._clean_cache()
        return obj

publicRenderingCacheFlusher = PublicRenderingCacheFlusher(VERSION, AnyMetaType, 100)

class GroupsService(BaseUpgrader):

    def upgrade(self, obj):
        zLOG.LOG('Silva', zLOG.INFO, 'Upgrade Groups Service ' + repr(obj))
        if not hasattr(obj, '_ip_groups'):
            obj._ip_groups = {}
        if not hasattr(obj, '_iprange_to_group'):
            obj._iprange_to_group = {}
        return obj

groupsService = GroupsService(VERSION, 'Groups Service', 120)

class CheckReservedIds(BaseUpgrader):

    def upgrade(self, obj):
        """Walk through the entire tree to find objects of which the id is not
        allowed, and return a list of the urls of those objects
        """
        object_list = obj.objectValues()
        while object_list:
            o = object_list[0]
            del object_list[0]
            if IContainer.providedBy(o):
                object_list.extend(o.objectValues())
            if not ISilvaObject.providedBy(o):
                continue
            old_id = o.getId()
            id = mangle.Id(o.aq_parent, old_id, allow_dup=1)
            if id.isValid():
                continue
            id.cook()
            while not id.isValid():
                id = mangle.Id(o.aq_parent, 'renamed_%s' % id, allow_dup=0)
            o.aq_parent.manage_renameObject(old_id, str(id))
            zLOG.LOG("Silva", zLOG.INFO,
                     'Invalid id %s found. Renamed to %s' % (repr(old_id), repr(id)),
                     'Location: %s' % o.absolute_url())

checkReservedIds = CheckReservedIds(VERSION, 'Silva Root', 40)

class BuryDemoObjectCorpses(BaseUpgrader):
    """
    This upgrades deletes all broken object which have been DemoObject
    instances before this class went away.
    """

    def upgrade(self, obj):
        # upgrade containers only
        if not IContainer.providedBy(obj):
            return obj

        broken_ids = obj.objectIds('Silva DemoObject')
        if broken_ids:
            zLOG.LOG('Silva',zLOG.DEBUG,
                     'found demo object corpses %s in %s' %\
                     (broken_ids, obj.absolute_url()))
            # the next statement assumes all IContainer inherit from Folder ...
            obj._ordered_ids = [ id for id in obj._ordered_ids
                                 if id not in broken_ids ]
            obj.manage_delObjects(broken_ids)
            # FIXME: how do we unindex broken object form the catalog?
        return obj

buryDemoObjectCorpses = BuryDemoObjectCorpses(VERSION, AnyMetaType, 90)
                     
class RefreshAll(BaseUpgrader):
    " refresh all products and installs SilvaDocument "

    def upgrade(self, root):
        zLOG.LOG('Silva', zLOG.INFO, 'install SilvaDocument')
        root.service_extensions.install('SilvaDocument')
        zLOG.LOG('Silva', zLOG.INFO, 'refresh all installed products') 
        root.service_extensions.refresh_all()
        return root

refreshAll = RefreshAll(VERSION, 'Silva Root', 130)
    
class ClearEditorCache(BaseUpgrader):
    " Clear widget cache and other caches "

    def upgrade(self, root):
        editor_service = getattr(root, 'service_editor', None)
        if editor_service is not None:
            cache = editor_service._get_editor_cache()
            zLOG.LOG('Silva', zLOG.INFO, 'Clear Editor Service cache')
            cache.clear()
        else:
            zLOG.LOG(
                'Silva', zLOG.INFO, 
                'No Editor Service found to clear the cache of')        
        return root

clearEditorCache = ClearEditorCache(VERSION, 'Silva Root', 140)

class CheckServiceMembers(BaseUpgrader):
    """ Set the '_allow_authentication_requests' attribute 
    on service_members if it isn't there yet.
    
    Copied from the upgrade_092 module
    """
    
    def upgrade(self, root):        
        sm = getattr(root, 'service_members', None)
        if sm is not None:
            zLOG.LOG('Silva', zLOG.INFO, 'Service Members checkup')
            if hasattr(sm, '_allow_subscription'):
                sm._allow_authentication_requests = sm._allow_subscription
                del sm._allow_subscription
            elif not hasattr(sm, '_allow_authentication_requests'):
                sm._allow_authentication_requests = 0
        return root

checkServiceMembers = CheckServiceMembers(VERSION, 'Silva Root', 150)

class SetAuthorInfoOnVersion(BaseUpgrader):
    """ Reset author info to version object for VersionedContent objects
    """
    
    def upgrade(self, obj):
        if IVersionedContent.providedBy(obj):
            versions = []
            versions.append(obj.get_viewable())
            versions.append(obj.get_previewable())
            versions.append(obj.get_editable())
            
            if obj._previous_versions:
                old_versions = []
                for version in obj._previous_versions:
                    id = str(version[0])
                    v = getattr(obj.aq_base, id, None)
                    versions.append(v)
                    #if hasattr(obj.aq_base, id):
                    #    versions.append(version)
                
            for version in versions:
                if version is not None:
                    version._last_author_info = getattr(obj, '_last_author_info', None)
                    version._last_author_userid = getattr(obj, '_last_author_userid', None)
        return obj

setAuthorInfoOnVersion = SetAuthorInfoOnVersion(VERSION, AnyMetaType, 20)

class RemoveOldMetadataIndexes(BaseUpgrader):
    """Remove all unused indexes placed there by installing some older
        metadata sets, in those way too much fields got indexed.
    """
    
    def upgrade(self, service_catalog):
        if service_catalog.id != 'service_catalog':
            return service_catalog
        zLOG.LOG('Silva', zLOG.INFO, 'Service Catalog cleanup')
        remove = ['silva-extrasubject', 'silva-extracomment', 
                    'silva-extracreationtime', 'silva-extramodificationtime', 
                    'silva-extracreator', 'silva-extralastauthor',
                    'silva-extralocation', 'silva-extracontactname',
                    'silva-extracontactemail']
        existing = service_catalog.indexes()
        for index in remove:
            if index in existing:
                service_catalog.delIndex(index)
                
        return service_catalog

removeOldMetadataIndexes = RemoveOldMetadataIndexes(VERSION, 'ZCatalog', 10)
    
class SetTitleFromIndexOnContainer(BaseUpgrader):
    """ Folder titles now are stored on the folder, 
    not on the index document. To fix this, we set the title of the 
    container to that of the index document, if it has one.
    """
    
    def upgrade(self, container):
        if not IContainer.providedBy(container):
            print 'This container object does not implement IContainer! (%s)' % repr(container)
            return container
        index = container.get_default() #getattr(container.aq_base, 'index', None)
        if index is None:
            return container
        try:
            title = index.get_title_editable()
            print 'Setting title to:', repr(title)
            container.set_title(title)
        except Exception, e:
            print 'Cannot set title on %s due to: %s' % (repr(container), e)
        return container

setTitleFromIndexOnContainer = SetTitleFromIndexOnContainer(
    VERSION, ['Silva Root', 'Silva Publication', 'Silva Folder'], 160)
    
