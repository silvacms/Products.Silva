## Script (Python) "backend_now_to_str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
import DateTime
dt = DateTime.DateTime()
return "%02d %s %04d %02d:%02d" % (dt.day(), dt.aMonth().lower(), dt.year(), dt.hour(), dt.minute())
