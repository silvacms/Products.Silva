##parameters=set_name,element_name
from Products.SilvaMetadata.Exceptions import BindingError

# This is a copy of views/public/get_metadata_element used in the SMI.
# FIXME: do we need a better location for this functionality?
#
# Get the data for a particular element of a particular set for
# the viewable version of this object.

request = container.REQUEST
content = context.get_viewable()

if content is None:
    return None

ms = context.service_metadata

try:
    binding = ms.getMetadata(content)
except BindingError, be:
    # No binding found..
    return None

if binding is None:
    return None

return binding.get(set_name, element_name)
