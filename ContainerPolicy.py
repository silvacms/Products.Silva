# Copyright (c) 2003 Infrae. All rights reserved.
# See also LICENSE.txt
# $Revision: 1.1 $

def create_index(container, id, title):
    """Create an index according to container policy.
    """
    # create an index object
    binding = container.service_metadata.getMetadata(container.get_publication())
    index_policy = binding.get('silva-publication',
                               element_id='index_policy')
    if index_policy == 'Silva Document':
        if container.service_extensions.is_installed('SilvaDocument'):
            container.manage_addProduct['SilvaDocument'].manage_addDocument(
                'index', title)
            container.index.sec_update_last_author_info()
    elif index_policy == 'Simple Index':
        pass
    else:
        # do nothing
        pass
