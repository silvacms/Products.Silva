## Script (Python) "get_type"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=node
##title=
##
# FIXME this one doesn't get node itself unlike all other get_type as context.REQUEST.node
# has changed. make all other get_type work like this.
if not node.hasAttribute('type'):
    return 'plain'
else:
    return node.getAttribute('type')
