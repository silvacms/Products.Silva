##parameters=set_name,element_name
# This is acopy of views/get_metadata_element used in the SMI.
# FIXME: do we need a better location for this functionality?
from Products.SilvaMetadata.Exceptions import BindingError

request = context.REQUEST
content = context.get_viewable()

if content is None:
    return None

ms = context.service_metadata

try:
    binding = ms.getMetadata(content)
except BindingError, be:
    # No binding found..
    return None

return binding.get(set_name, element_name)
