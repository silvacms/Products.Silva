#Copyright (c) 2002-2007 Infrae. All rights reserved.
#See also LICENSE.txt
"""
Purpose:

  - Metadata Import/Export Integration w/ Silva.

  - Content Type Registration For Metadata

      Silva maintains a dichotomy between content types addable in the smi
      and the actual content objects in order to implement its versioning
      system. Because of this using the silva_addables_all for determining
      content types for the metadata system is inappropriate, as metadata
      needs to be versioned along with actual content.

$Id: Metadata.py,v 1.26 2006/01/24 16:14:12 faassen Exp $    
"""
from Products.SilvaMetadata.Compatibility import registerTypeForMetadata
from Products.SilvaMetadata.Compatibility import getToolByName, getContentType
from Products.SilvaMetadata.Import import import_metadata
from Products.SilvaMetadata.Access import registerAccessHandler, invokeAccessHandler
from Products.SilvaMetadata.Access import default_accessor
from Products.SilvaMetadata.Initialize import registerInitHandler
from Products.SilvaMetadata import Binding
from Products.Silva.Versioning import Versioning

from interfaces import IVersionedContent

#################################
### handlers and thin wrappers for metadata

def export_metadata(content, context):
    out = context.f 
    metadata_service = getToolByName(content, 'portal_metadata')
    binding = metadata_service.getMetadata(content)
    out.write( binding.renderXML() )
    
    return None

def import_metadata_handler(container, content, node):
    if IVersionedContent.providedBy(content):
        # the current import code all seems to create an initial version
        # of '0' on import
        version = getattr(content, '0')
        import_metadata(version, node)
    else:
        import_metadata(content, node)

    return None

def ghost_access_handler(tool, content_type, content):
    target_content = content.get_haunted_unrestricted()
    if target_content is None:
        return None
    target_content = target_content.get_viewable()
    if target_content is None:
        return None
    ct = getContentType(target_content)
    return default_accessor(tool, ct, target_content, read_only=True)
        
def ghostfolder_access_handler(tool, content_type, content):
    haunted_folder = content.get_haunted_unrestricted()
    if haunted_folder is None:
        return None
    ct = getContentType(haunted_folder)
    return default_accessor(tool, ct, haunted_folder, read_only=True)
    

#################################
### registration

def initialize_metadata():
    register_import_initializers()
    register_access_handlers()
    register_initialize_handlers()

def register_import_initializers():
    """
    integrate metadata importing with the silva imports
    """
    from Products.Silva.ImporterRegistry import register_initializer
    register_initializer(import_metadata_handler, default=1)

def register_access_handlers():
    """
    deal with special silva content types that need specialized
    metadata handling
    """
    from Products.Silva.Ghost import GhostVersion
    from Products.Silva.GhostFolder import GhostFolder
    registerAccessHandler(GhostVersion.meta_type, ghost_access_handler)
    registerAccessHandler(GhostFolder.meta_type, ghostfolder_access_handler)

def register_initialize_handlers():
    """Set initialize handlers which set mutation triggers on everything
    for the silva-content set. This takes care of sidebar cache invalidation 
    upon (short)title changes. 
    """
    # use None for content type registers initializer for all content
    # types
    registerInitHandler(None, _initialize_handler)

def _initialize_handler(object, bind_data):
    set_id = 'silva-content'
    set_triggers = {
        'maintitle': 'titleMutationTrigger',
        'shortitle': 'titleMutationTrigger',
        }

    bind_data[Binding.MutationTrigger] = {set_id: set_triggers}
