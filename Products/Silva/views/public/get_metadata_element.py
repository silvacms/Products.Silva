##parameters=set_name,element_name
request = context.REQUEST
model = request.model
version = model.get_viewable()
ms = context.service_metadata

return ms.getMetadataValue(version, set_name, element_name)
