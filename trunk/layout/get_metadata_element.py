##parameters=set_name,element_name

# This is a copy of views/public/get_metadata_element used in the SMI.
#
# Get the data for a particular element of a particular set for
# the viewable version of this object.

content = context.get_viewable()

if content is None:
    return None

return context.service_metadata.getMetadataValue(
    content, set_name, element_name)
