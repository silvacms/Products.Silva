##parameters=set_name,element_name

# Get the data for a particular element of a particular set for
# the most current version of this object.

request = context.REQUEST
model = request.model
content = model.get_previewable()

if content is None:
    return None

return context.service_metadata.getMetadataValue(
    content, set_name, element_name)
