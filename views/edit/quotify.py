## Script (Python) "quotify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=input
##title=
##
left_quote = '&laquo;'
right_quote = '&raquo;'

return '%s%s%s' % (left_quote, input, right_quote)
