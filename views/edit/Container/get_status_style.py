## Script (Python) "get_status_style"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=obj
##title=
##
if obj.implements_versioning():
   status = obj.get_next_version_status()
   if status == 'not_approved':
       return 'redlink'
   elif status == 'request_pending':
       return 'yellowlink'
   elif status == 'approved':
       return 'greenlink'
   elif status == 'no_next_version' and obj.get_public_version_status() == 'closed':
       return 'graylink'
   elif status == 'no_next_version':
       return 'bluelink'
   else:
       return 'blacklink' # should never happen
else:
   return 'blacklink'
