## Script (Python) "get_start_container"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Lookup the container to start listing assets
##
image = context.content()
if image is None:
    # no image selected, or image is broken: start in the current container
    return context.REQUEST.node.get_container()
else:
    return image.get_container()
