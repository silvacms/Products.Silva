## Script (Python) "clear_message"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
context.REQUEST.SESSION['message'] = ''
context.REQUEST.SESSION['message_type'] = ''
