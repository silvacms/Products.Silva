## Script (Python) "content"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
content = context.text_content()
if content.strip() == '':
    return '&nbsp;'
return content
