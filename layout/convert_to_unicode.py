## Script (Python) "convert_to_unicode"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=incoming,charset='UTF-8'
##title=
##
"""Python script to convert incoming data to Unicode

Incoming data can either be a single or a multi-dimension datatype.
"""

def convert_tuple(t, charset):
    """Convert a tuple to unicode (recursive)"""
    new = []
    for item in t:
        new.append(convert_item(item, charset))
    return tuple(new)

def convert_list(l, charset):
    """Convert a list to unicode (recursive)"""
    new = []
    for item in l:
        new.append(convert_item(item, charset))
    return new

def convert_dict(d, charset):
    """Convert a dict to unicode (recursive)"""
    new = {}
    for k, v in d.items():
        new[convert_item(k, charset)] = convert_item(v, charset)
    return new

# yes, it's nasty, but our scripts always expect a string back...
def convert_item(i, charset):
    """Convert an item to unicode"""
    if same_type(i, []):
        return u'[\'%s\']' % '\', \''.join(convert_list(i, charset))
    elif same_type(i, ()):
        return u'(\'%s\')' % '\', \''.join(convert_tuple(i, charset))
    elif same_type(i, {}):
        return u'{\'%s\'}' % "', '".join(["%s': '%s" % (k, v) for (k, v) in convert_dict(i, charset).items()])
    elif same_type(i, u''):
        return i
    elif same_type(i, ''):
        return unicode(i, charset)
    else:
        # basic datatype or unknown datatype, convert to
        # unicode string and return
        return unicode(str(i), charset)

return convert_item(incoming, charset)

