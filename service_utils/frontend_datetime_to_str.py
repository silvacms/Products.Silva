## Script (Python) "frontend_datetime_to_str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dt
##title=
##
return "%02d %s %04d %02d:%02d" % (dt.day(), dt.aMonth(), dt.year(), dt.hour(), dt.minute())
