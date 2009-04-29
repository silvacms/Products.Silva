# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.SilvaMetadata.Access import registerAccessHandler
from Products.SilvaMetadata.Access import default_accessor
from Products.SilvaMetadata.Initialize import registerInitHandler
from Products.SilvaMetadata import Binding


#################################
### handlers and thin wrappers for metadata

def ghost_access_handler(tool, content_type, content):
    target_content = content.get_haunted_unrestricted()
    if target_content is None:
        return None
    target_content = target_content.get_viewable()
    if target_content is None:
        return None
    ct = target_content.meta_type
    return default_accessor(tool, ct, target_content, read_only=True)

def ghostfolder_access_handler(tool, content_type, content):
    haunted_folder = content.get_haunted_unrestricted()
    if haunted_folder is None:
        return None
    ct = haunted_folder.meta_type
    return default_accessor(tool, ct, haunted_folder, read_only=True)


#################################
### registration

def initialize_metadata():
    register_access_handlers()
    register_initialize_handlers()

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
