##parameters=set_name,element_name
from Products.SilvaMetadata.Exceptions import BindingError

# Get the data for a particular element of a particular set for
# the editable version of this object.

request = context.REQUEST
model = request.model
content = model.get_previewable()

if content is None:
    return None

ms = context.service_metadata

try:
    binding = ms.getMetadata(content)
except BindingError, be:
    # No binding found..
    return None

return binding.get(set_name, element_name)
