##parameters=set_name,element_name
from Products.SilvaMetadata.Exceptions import BindingError

# Get the data for a particular element of a particular set for
# the viewable version of this object.

request = context.REQUEST
#content = context.get_viewable()
content = request.model

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
