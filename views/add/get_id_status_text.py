##parameters=id, status_code

from Products.Silva.helpers import IdCheckValues
view = context

if status_code == IdCheckValues.ID_CONTAINS_BAD_CHARS:
    return """Sorry, strange characters are in the id. It should only contain letters, digits and &#8216;_&#8217; or &#8216;-&#8217; or &#8216;.&#8217;<br />
Spaces are not allowed in Internet addresses, and the id should start with a letter or digit."""

elif status_code == IdCheckValues.ID_RESERVED_PREFIX:
    # FIXME: needs to know about the prefix
    prefix = id.split('_')[0]+'_'
    return """Sorry, ids starting with %s are reserved for internal use.<br />
Please use another id.""" % view.quotify(prefix)

elif status_code == IdCheckValues.ID_RESERVED:
    return """Sorry, the id %s is reserved for internal use.<br />
Please use another id.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_IN_USE_CONTENT:
    return """There is already an object with the id %s in this folder.<br />
Please use a different one.""" % view.quotify(id)

elif status_code == IdCheckValues.ID_IN_USE_ASSET:
    return """There is already an asset with the id %s in this folder.<br />
Please use another id.""" % view.quotify(id)

# this should not happen
return """(Internal Error): An invalid status %s occured while checking the id %s.<br />
Please contact the person responsible for this Silva installation or file a bug report.""" % (view.quotify(status_code), view.quotify(id))

