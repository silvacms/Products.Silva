## Script (Python) "get_start_container"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Lookup the container to start listing assets
##
request = context.REQUEST
model = request.model
version = model.get_editable()
status = version.get_link_status()
if status == version.LINK_OK:
    content = version.get_haunted()
    if content is not None:
        return content.get_container()
return model.get_container()

