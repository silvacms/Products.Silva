## Script (Python) "get_type"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
if not node.hasAttribute('type'):
    return 'normal'
else:
    return node.getAttribute('type')
