## Script (Python) "get_list_type"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
node = context.REQUEST.node
if node.hasAttribute('type'):
    return node.getAttribute('type')
else:
    return 'disc'
