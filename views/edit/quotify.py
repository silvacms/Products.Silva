## Script (Python) "quotify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=input
##title=
##
left_quote = '&#xab;'
right_quote = '&#xbb;'

return u'%s%s%s' % (left_quote, input, right_quote)
