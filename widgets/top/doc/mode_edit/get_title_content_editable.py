## Script (Python) "get_title_content_editable"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
return context.REQUEST.node.get_content().get_title_editable()
