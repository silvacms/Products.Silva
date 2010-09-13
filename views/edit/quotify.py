## Script (Python) "quotify"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=input
##title=
##
left_quote = u'"'
right_quote = u'"'

return u'%s%s%s' % (left_quote, unicode(input), right_quote)
