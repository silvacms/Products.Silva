##parameters=set_name,element_name

# This is a copy of views/public/get_metadata_element used in the SMI.
# FIXME: do we need a better location for this functionality?
#
# One way to get to the get_metadata_element in the "public" view of
# a Silva object is this:
#
#   method = obj.public['get_metadata_element']
#   data = method(setname, elementname)
#
# Get the data for a particular element of a particular set for
# the viewable version of this object.

content = context.get_viewable()

if content is None:
    return None

return context.service_metadata.getMetadataValue(
    content, set_name, element_name)
