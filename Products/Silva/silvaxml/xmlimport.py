# Copyright (c) 2003-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from StringIO import StringIO
import logging
import warnings

from five import grok
from zope.event import notify

from DateTime import DateTime

from silva.core import conf as silvaconf
from silva.core.interfaces import (ISilvaObject, IImportSettings,
    ISilvaXMLImportHandler)
from silva.core.interfaces.events import ContentImported, IContentImported
from silva.core.references.reference import canonical_path
from silva.core.services.interfaces import ICataloging
from silva.core.upgrade.silvaxml import upgradeXMLOnFD
from sprout.saxext import xmlimport, collapser
from Products.Silva.silvaxml import ImportExportSettingsErrors


NS_URI = 'http://infrae.com/namespace/silva'

silvaconf.namespace(NS_URI)

theXMLImporter = xmlimport.Importer()
logger = logging.getLogger('silva.xml')

class ImportReferenceError(xmlimport.XMLImportError):
    """The imported content refer to a non-existing other imported
    content.
    """


@grok.subscribe(ISilvaObject, IContentImported)
def reindex_import_content(content, event):
    """Re-index imported content.
    """
    ICataloging(content).index()


def parse_date(date):
    if date:
        return DateTime(date)
    return None


def resolve_path(setter, info, target_path):
    """Resolve target_path from root, and set it using setter.
    """
    if not target_path:
        # target_path == '' means the reference is broken.
        return
    root = info.importRoot()
    imported_target_path = info.getImportedPath(canonical_path(target_path))
    if imported_target_path is None:
        raise ImportReferenceError(target_path)
    path = map(str, imported_target_path.split('/'))
    target = root.unrestrictedTraverse(path)
    setter(target)


class SilvaBaseHandler(xmlimport.BaseHandler):
    """Base class to writer an XML importer for a Silva content. It
    provides helpers to set Silva properties and metadatas.
    """
    grok.baseclass()
    grok.implements(ISilvaXMLImportHandler)

    def __init__(self, parent, parent_handler, settings=None, info=None):
        xmlimport.BaseHandler.__init__(
            self, parent, parent_handler, settings, info)
        self._metadata_set = None
        self._metadata_key = None
        self._metadata = {}
        self._metadata_multivalue = False
        self._workflow = {}
        self.__id_result = None
        self.__id_original = None

    # MANIPULATORS

    def storeMetadata(self):
        content = self.result()
        metadata_service = content.service_metadata
        binding = metadata_service.getMetadata(content)
        if binding is not None:
            for set_id, elements in self._metadata.items():
                set_obj = binding.collection.get(set_id, None)
                if set_obj is None:
                    logger.warn(
                        u"unknown metadata set %s present in import file." % (
                            set_id,))
                    continue
                element_names = elements.keys()
                for element_name in element_names:
                    if not hasattr(set_obj.aq_explicit, element_name):
                        logger.warn(
                            u"unknown metadata element %s in set %s." %
                            (element_name, set_id))
                        continue
                    field = set_obj.getElement(element_name).field

                    # Set data
                    errors = binding._setData(
                        namespace_key=set_obj.metadata_uri,
                        data={
                            element_name: field.validator.deserializeValue(
                                field, elements[element_name])},
                        reindex=0)
                    if errors:
                        logger.warn(
                            u"value %s is not allowed for %s in set %s." % (
                                elements[element_name], element_name, set_id))

    def notifyImport(self):
        """Notify the event system that the content have been
        imported. This must be the last item done.
        """
        self.getInfo().addAction(notify, [ContentImported(self.result())])

    def setResultId(self, uid):
        self.__id_result = uid
        self.setResult(getattr(self.parent(), uid))
        # This should be done by the importer in the processing of
        # end. However we set it here for backward compatiblity
        # issues.
        self.getInfo().addImportedPath(
            self.getOriginalPhysicalPath(), self.getResultPhysicalPath())

    def setOriginalId(self, uid):
        self.__id_original = uid

    def getResultPhysicalPath(self):
        parent = self.parentHandler()
        if parent is None:
            return []
        path = parent.getResultPhysicalPath()
        path.append(self.__id_result)
        return path

    def getOriginalPhysicalPath(self):
        parent = self.parentHandler()
        if parent is None:
            return []
        path = parent.getOriginalPhysicalPath()
        path.append(self.__id_original or self.__id_result)
        return path

    def setMetadataKey(self, key):
        self._metadata_key = key

    def setMetadata(self, set, key, value):
        if value is not None:
            value = value.encode('utf-8')
            if self.metadataMultiValue():
                if self._metadata[set].has_key(key):
                    self._metadata[set][key].append(value)
                else:
                    self._metadata[set][key] = [value]
            else:
                self._metadata[set][key] = value

    def setMetadataSet(self, set):
        self._metadata_set = set
        self._metadata[set] = {}

    def setMetadataMultiValue(self, trueOrFalse):
        self._metadata_multivalue = trueOrFalse

    def setWorkflowVersion(
        self, version_id, publication_time, expiration_time, status):

        self.parentHandler()._workflow[version_id.strip()] = (
            parse_date(publication_time),
            parse_date(expiration_time),
            status)

    def getWorkflowVersion(self, version_id):
        return self.parentHandler()._workflow[version_id]

    def storeWorkflow(self):
        content = self.result()
        version_id = content.id
        publicationtime, expirationtime, status = self.getWorkflowVersion(
            version_id)
        version = (version_id, publicationtime, expirationtime)
        if status == 'unapproved':
            self.parent()._unapproved_version = version
        elif status == 'approved':
            self.parent()._approved_version = version
        elif status == 'public':
            self.parent()._public_version = version
        else:
            previous_versions = self.parent()._previous_versions or []
            previous_versions.append(version)
            self.parent()._previous_versions = previous_versions

    # ACCESSORS

    def metadataKey(self):
        return self._metadata_key

    def metadataSet(self):
        return self._metadata_set

    def getMetadata(self, set, key):
        return self._metadata[set].get(key)

    def metadataMultiValue(self):
        return self._metadata_multivalue

    def generateOrReplaceId(self, uid=None):
        if uid is None:
            uid = self.getData('id')
        parent = self.parent()
        self.setOriginalId(uid)
        if self.settings().replaceObjects():
            if uid in parent.objectIds():
                parent.manage_delObjects([uid])
            return uid
        else:
            return generateUniqueId(uid, parent)


class SilvaExportRootHandler(SilvaBaseHandler):

    grok.name('silva')

    def getResultPhysicalPath(self):
        return []

    def getOriginalPhysicalPath(self):
        return []


class FolderHandler(SilvaBaseHandler):

    grok.name('folder')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'folder'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addFolder(uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'folder'):
            self.storeMetadata()
            self.notifyImport()


class PublicationHandler(SilvaBaseHandler):

    grok.name('publication')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'publication'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addPublication(
                uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'publication'):
            self.storeMetadata()
            self.notifyImport()


class AutoTOCHandler(SilvaBaseHandler):

    grok.name('auto_toc')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'auto_toc'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addAutoTOC(
                uid, '')
            self.setResultId(uid)
            obj = getattr(self.parent(),uid)
            #not all imported TOCs will have these, so only set if they do
            if (attrs.get((None,'depth'),None)):
                obj.set_toc_depth(int(attrs[(None,'depth')]))
            if (attrs.get((None,'types'),None)):
                obj.set_local_types(attrs[(None, 'types')].split(','))
            if (attrs.get((None,'display_desc_flag'),None)):
                obj.set_display_desc_flag(attrs[(None,'display_desc_flag')]=='True')
            if (attrs.get((None,'show_icon'),None)):
                obj.set_show_icon(attrs[(None,'show_icon')]=='True')
            if (attrs.get((None,'sort_order'),None)):
                obj.set_sort_order(attrs[(None,'sort_order')])

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'auto_toc'):
            self.storeMetadata()
            self.notifyImport()


class IndexerHandler(SilvaBaseHandler):

    grok.name('indexer')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'indexer'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addIndexer(
                uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'indexer'):
            #self.setMaintitle()
            self.storeMetadata()
            self.getInfo().addAction(self.result().update, [])
            self.notifyImport()


class VersionHandler(SilvaBaseHandler):

    grok.name('version')

    def getOverrides(self):
        return {
            (NS_URI, 'status'): make_character_handler('status', self),
            (NS_URI, 'publication_datetime'): make_character_handler(
                'publication_datetime', self),
            (NS_URI, 'expiration_datetime'): make_character_handler(
                'expiration_datetime', self),
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'version'):
            self.setData('id', attrs[(None, 'id')])

    def endElementNS(self, name, qname):
        self.setWorkflowVersion(
            self.getData('id'),
            self.getData('publication_datetime'),
            self.getData('expiration_datetime'),
            self.getData('status'))


class SetHandler(SilvaBaseHandler):

    grok.name('set')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'set'):
            self.parentHandler().setMetadataSet(attrs[(None, 'id')])
        elif name != (NS_URI, 'value'):
            self.parentHandler().setMetadataKey(name[1])
        else:
            self.parentHandler().setMetadataMultiValue(True)
        self.setResult(None)

    def characters(self, chars):
        if self.parentHandler().metadataKey() is not None:
            self._chars = chars.strip()

    def endElementNS(self, name, qname):
        if name != (NS_URI, 'set'):
            value = getattr(self, '_chars', None)

            if self.parentHandler().metadataKey() is not None:
                self.parentHandler().setMetadata(
                    self.parentHandler().metadataSet(),
                    self.parentHandler().metadataKey(),
                    value)
        if name != (NS_URI, 'value'):
            self.parentHandler().setMetadataKey(None)
            self.parentHandler().setMetadataMultiValue(False)
        self._chars = None


class GhostHandler(SilvaBaseHandler):

    grok.name('ghost')

    def getOverrides(self):
        return {(NS_URI, 'content'): GhostContentHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'ghost'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addGhost(
                uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'ghost'):
            self.notifyImport()


class GhostContentHandler(SilvaBaseHandler):

    def getOverrides(self):
        return {
            (NS_URI, 'haunted'): make_character_handler('haunted', self),
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                uid = attrs[(None, 'version_id')].encode('utf8')
                self.parent().manage_addProduct['Silva'].manage_addGhostVersion(
                    uid, '')
                self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            haunted = self.getData('haunted')
            if haunted is None:
                logger.error('invalid ghost at %s' %
                             '/'.join(self.result().getPhysicalPath()))
            else:
                info = self.getInfo()
                info.addAction(
                    resolve_path,
                    [self.result().set_haunted, info, haunted])
            updateVersionCount(self)
            self.storeWorkflow()


class GhostFolderHandler(SilvaBaseHandler):

    grok.name('ghost_folder')

    def getOverrides(self):
        return {
            (NS_URI, 'haunted'): make_character_handler('haunted', self),
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'ghost_folder'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addGhostFolder(
                uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'ghost_folder'):
            folder = self.result()
            haunted = self.getData('haunted')
            if haunted is None:
                logger.error('invalid ghost folder at %s' %
                             '/'.join(folder.getPhysicalPath()))
            else:
                info = self.getInfo()
                folder = self.result()
                info.addAction(
                    resolve_path,
                    [folder.set_haunted, info, haunted])
                info.addAction(folder.haunt, [])
            self.notifyImport()


class NoopHandler(SilvaBaseHandler):

    def isElementAllowed(self, name):
        return False


class LinkHandler(SilvaBaseHandler):

    grok.name('link')

    def getOverrides(self):
        return {(NS_URI, 'content'): LinkVersionHandler}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'link'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            self.parent().manage_addProduct['Silva'].manage_addLink(
                uid, '', no_default_version=True)
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'link'):
            self.notifyImport()


class LinkVersionHandler(SilvaBaseHandler):

    def getOverrides(self):
        return {
            (NS_URI, 'url'): make_character_handler('url', self),
            (NS_URI, 'target'): make_character_handler('target', self),
            }

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'content'):
            if attrs.has_key((None, 'version_id')):
                uid = attrs[(None, 'version_id')].encode('utf8')
                self.parent().manage_addProduct['Silva'].manage_addLinkVersion(
                    uid, '')
                self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'content'):
            link = self.result()
            url = self.getData('url')
            if url is not None:
                link.set_relative(False)
                link.set_url(url)
            else:
                link.set_relative(True)
                target = self.getData('target')
                info = self.getInfo()
                info.addAction(
                    resolve_path, [link.set_target, info, target])
            updateVersionCount(self)
            self.storeMetadata()
            self.storeWorkflow()


class ImageHandler(SilvaBaseHandler):
    """Import a Silva image.
    """
    grok.name('image_asset')

    def getOverrides(self):
        return {(NS_URI, 'asset_id'): make_character_handler('zip_id', self),}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'image_asset'):
            self.setData('id', attrs[(None, 'id')])
            self.setData('web_format', attrs.get((None, 'web_format')))
            self.setData('web_scale', attrs.get((None, 'web_scale')))
            self.setData('web_crop', attrs.get((None, 'web_crop')))

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'image_asset'):
            uid = self.generateOrReplaceId()
            import_image = self.getInfo().getFileFromZIP(
                'assets/' + self.getData('zip_id'))
            self.parent().manage_addProduct['Silva'].manage_addImage(
                uid, '', import_image)
            self.setResultId(uid)

            web_format = self.getData('web_format')
            web_scale = self.getData('web_scale')
            web_crop = self.getData('web_crop')
            if web_format or web_scale or web_crop:
                self.result().set_web_presentation_properties(
                    web_format, web_scale, web_crop)

            self.storeMetadata()
            self.notifyImport()


class FileHandler(SilvaBaseHandler):
    """Import a Silva File.
    """
    grok.name('file_asset')

    def getOverrides(self):
        return {(NS_URI, 'asset_id'): make_character_handler('zip_id', self),}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'file_asset'):
            self.setData('id', attrs[(None, 'id')])

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'file_asset'):
            uid = self.generateOrReplaceId()
            import_file = self.getInfo().getFileFromZIP(
                'assets/' + self.getData('zip_id'))
            self.parent().manage_addProduct['Silva'].manage_addFile(
                uid, '', import_file)
            self.setResultId(uid)
            self.storeMetadata()
            self.notifyImport()


class UnknownContentHandler(SilvaBaseHandler):
    """Importer for content which have been exported in a ZEXP.
    """
    grok.name('unknown_content')

    def getOverrides(self):
        return {(NS_URI, 'zexp_id'): make_character_handler('zexp_id', self),}

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'unknown_content'):
            self.setData('id', attrs[(None, 'id')])

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'unknown_content'):
            info = self.getInfo()
            import_file = info.getFileFromZIP(
                'zexps/' + self.getData('zexp_id'))
            root = self.getInfo().importRoot()
            content = root._p_jar.importFile(import_file)
            uid = self.generateOrReplaceId()
            self.parent()._setObject(str(uid), content)
            self.setResultId(uid)
            self.notifyImport()


def make_character_handler(name, handler):

    class CharacterHandler(SilvaBaseHandler):

        def __repr__(self):
            return '<XMLImportHandler for characters of %s>' % name

        def characters(self, chars):
            return handler.setData(name, chars.strip())

    return CharacterHandler


class ImportSettings(xmlimport.BaseSettings, ImportExportSettingsErrors):
    grok.implements(IImportSettings)

    def __init__(self, replace_objects=False, request=None):
        xmlimport.BaseSettings.__init__(
            self,
            ignore_not_allowed=True,
            import_filter_factory=collapser.CollapsingHandler)
        self._replace_objects = replace_objects
        self.request = request

    def replaceObjects(self):
        return self._replace_objects


class ImportInfo(object):
    """Manage information about the import.
    """

    def __init__(self):
        self.__zip_file = None
        self.__actions = []
        self.__import_root = None
        self.__paths = {}

    def addImportedPath(self, original, imported):
        """Remenber that the original imported path as been imported
        with the given new one.
        """
        self.__paths[u'/'.join(original)] = u'/'.join(imported)

    def getImportedPath(self, path):
        """Return an imported path for the given original one.
        """
        return self.__paths.get(path)

    def setImportRoot(self, root):
        self.__import_root = root

    def importRoot(self):
        """Return import root.
        """
        return self.__import_root

    def setZIPFile(self, file):
        """Set imported ZIP.
        """
        self.__zip_file = file

    def getFileFromZIP(self, filename):
        """Return content of a file from the ZIP
        """
        if self.__zip_file is None:
            return None
        return StringIO(self.__zip_file.read(filename))

    def addAction(self, action, args):
        """Add an action to be executed in a later stage.
        """
        self.__actions.append((action, args))

    def runActions(self, clear=True):
        """Run scheduled actions.
        """
        for action, args in self.__actions:
            action(*args)
        if clear is True:
            del self.__actions[:]


def generateUniqueId(org_id, context):
        i = 0
        id = org_id
        ids = context.objectIds()
        while id in ids:
            i += 1
            add = ''
            if i > 1:
                add = str(i)
            id = 'import%s_of_%s' % (add, org_id)
        return id


def updateVersionCount(versionhandler):
    # The parent of a version is a VersionedContent object. This VC object
    # has an _version_count attribute to keep track of the number of
    # existing version objects and is the used to determine the id for a
    # new version. However, after importing, this _version_count has the
    # default value (1) and thus should be updated to reflect the highest
    # id of imported versions (+1 of course :)
    parent = versionhandler.parent()
    version = versionhandler.result()
    id = version.id
    try:
        id = int(id)
    except ValueError:
        # I guess this is the only reasonable thing to do - apparently
        # this id does not have any numerical 'meaning'.
        return
    vc = max(parent._version_count, (id + 1))
    parent._version_count = vc


def importFromFile(source_file, context, info=None, replace=False,
        request=None):
    source_file = upgradeXMLOnFD(source_file)

    settings = ImportSettings(replace_objects=replace, request=request)
    info = info or ImportInfo()
    info.setImportRoot(context)
    theXMLImporter.importFromFile(
        source_file,
        result=context,
        settings=settings,
        info=info)
    # run post-processing actions
    info.runActions()
    return context


def importReplaceFromFile(source_file, context, info=None, request=None):
    warnings.warn('use directly importFromFile with replace=True. '
                  'importeReplaceFromFile will be removed in Silva 2.4.',
                  DeprecationWarning, stacklevel=2)
    importFromFile(source_file, context, info=info,
        replace=True, request=request)


