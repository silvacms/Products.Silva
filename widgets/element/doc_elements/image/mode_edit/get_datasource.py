## Script (Python) "get_datasource"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
request = context.REQUEST
node = request.node
path = node.getAttribute('path')
datasource = None
if path:
    try:
        datasource = node.restrictedTraverse(path)
    except (KeyError, AttributeError):
        # datasource reference is broken (i.e. renamed)
        pass

return datasource