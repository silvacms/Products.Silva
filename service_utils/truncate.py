## Script (Python) "truncate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=content, length
##title=
##
if len(content) <= length:
    return content

return content[:(length - 3)] + '...'
