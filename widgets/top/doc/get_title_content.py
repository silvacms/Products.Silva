## Script (Python) "get_title_content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
content = context.REQUEST.node.get_content()
return content.output_convert_html(content.get_title())
