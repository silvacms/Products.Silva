## Script (Python) "get_title_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
from Products.Silva.helpers import escape_entities
content = context.REQUEST.node.get_content()
return escape_entities(content.get_title_editable())
