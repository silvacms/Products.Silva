## Script (Python) "backend_short_datetime_to_str2"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dt
##title=
##
# compressed datetime display, to keep table columns as thin as possible 
if dt is not None:
    return "%02d.%s.%s&middot;%02d:%02d" % (dt.day(), dt.aMonth().lower(), dt.yy(), dt.hour(), dt.minute())
else:
    return ''
