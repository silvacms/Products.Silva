# This is a copy of views/public/get_metadata_element used in the SMI.
#
# Get the data for a particular element of a particular set for
# the viewable version of this object.

content = context.get_viewable()

if content is None:
    return None

binding = context.service_metadata.getMetadata(content)
return binding.get(set_name, element_id=element_name)
