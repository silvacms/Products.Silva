##parameters=set_name,element_name
from Products.SilvaMetadata.Exceptions import BindingError

# Get the data for a particular element of a particular set for
# the most current version of this object.
# This is normally the editable one; as Readers cann ot access it,
# the previewable is used insetad, which usually the editable one
# (except in cases where there is no editable yet).

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
if binding is None:
    return None

return binding.get(set_name, element_name)
