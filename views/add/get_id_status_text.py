##parameters=id
# return mangle error message
# id: mangle.Id instance
# returns string

from Products.Silva import mangle
from Products.Silva.i18n import translate as _
from zope.i18n import translate

# backward compatibility (for now)
if same_type(id, ""):
    id = mangle.Id(id)

status_code = id.validate()

if status_code == id.CONTAINS_BAD_CHARS:
    return translate(_("""Sorry, strange characters are in the id. It should only
        contain letters, digits and &#8216;_&#8217; or &#8216;-&#8217; or 
        &#8216;.&#8217; Spaces are not allowed in Internet addresses, 
        and the id should start with a letter or digit."""))
elif status_code == id.RESERVED_PREFIX:
    # FIXME: needs to know about the prefix
    prefix = str(id).split('_')[0]+'_'
    message = _("Sorry, ids starting with ${prefix} are reserved for "
                "internal use. Please use another id.",
                mapping={'prefix': context.quotify(prefix)})
    return translate(message)
elif status_code == id.RESERVED:
    message = _("Sorry, the id ${id} is reserved for internal use. "
                "Please use another id.", mapping={'id': context.quotify(id)})
    return translate(message)
elif status_code == id.IN_USE_CONTENT:
    message = _("There is already an object with the id ${id} in this "
                "folder. Please use a different one.",
                mapping={'id': context.quotify(id)})
    return translate(message)
elif status_code == id.IN_USE_ASSET:
    message = _("There is already an asset with the id ${id} in this "
                "folder. Please use another id.",
                mapping={'id': context.quotify(id)})
    return translate(message)
elif status_code == id.RESERVED_POSTFIX:
    message = _("Sorry, the id ${id} ends with invalid characters. Please "
                "use another id.", mapping={'id': context.quotify(id)})
    return translate(message)
elif status_code == id.IN_USE_ZOPE:
    message = _("Sorry, the id ${id} is already in use by a Zope object. "
                "Please use another id.",
                mapping={'id': context.quotify(id)})
    return translate(message)

# this should not happen
message = _("(Internal Error): An invalid status ${status_code} occured "
            "while checking the id ${id}. Please contact the person "
            "responsible for this Silva installation or file a bug report.""",
            mapping={
                     'status_code': context.quotify(status_code),
                     'id': context.quotify(id)})

return translate(message)
