## Script (Python) "backend_datetime_to_str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dt
##title=
##
if dt is not None:
    return "%02d %s %04d" % (dt.day(), dt.aMonth().lower(), dt.year())
else:
    return ''

