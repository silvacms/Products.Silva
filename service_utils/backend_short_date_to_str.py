## Script (Python) "backend_short_date_to_str"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=dt
##title=
##
if dt is not None:
    return "%02d-%02d-%04d" % (dt.day(), dt.month(), dt.year())
else:
    return ''
