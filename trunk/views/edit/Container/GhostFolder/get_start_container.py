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
assert model.meta_type == 'Silva Ghost Folder', '%r is no ghost folder' % model
status = model.get_link_status()
if status == model.LINK_OK:
    content = model.get_haunted()
    if content is not None:
        return content.aq_parent.get_container()
return model.aq_parent.get_container()

